import os
import sys
import json
import argparse
import torch



from datasets import load_dataset
from transformers import (
    T5ForConditionalGeneration,
    T5TokenizerFast,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq,
    TrainerCallback
)

class EpochInferenceCallback(TrainerCallback):
    def __init__(self, model, tokenizer, device):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.last_train_loss = "N/A"
        self.last_eval_loss = "N/A"

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is not None:
            if "loss" in logs:
                self.last_train_loss = f"{logs['loss']:.4f}"
                print(f"  [Step {state.global_step}] Train Loss: {self.last_train_loss}")
            if "eval_loss" in logs:
                self.last_eval_loss = f"{logs['eval_loss']:.4f}"
                print(f"  [Step {state.global_step}] Eval Loss: {self.last_eval_loss}")

    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"\n" + "="*60)
        print(f"📊 EPOCH {state.epoch:.0f} STATUS SUMMARY")
        print(f"  Training Loss   : {self.last_train_loss}")
        print(f"  Validation Loss : {self.last_eval_loss}")
        print("="*60)
        print("🔮 Intermediate Test Predictions:")
        
        test_cases = [
            "rainy day",
            "happy today",
            "food awful"
        ]
        
        self.model.eval()
        for gloss in test_cases:
            input_text = f"translate gloss to emoji: {gloss.strip().lower()}"
            inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_length=32)
            pred = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"  Input: {gloss}")
            print(f"  Pred : {pred if pred else '[empty]'}")
        print("="*60 + "\n")
        self.model.train()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Fine-tune FLAN-T5-base for emoji prediction.")
    parser.add_argument("--train_path", type=str, default="data/train.json", help="Path to train JSON file")
    parser.add_argument("--val_path", type=str, default="data/val.json", help="Path to val JSON file")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size per device")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--output_dir", type=str, default="models/flan_emoji", help="Directory to save the best model")
    parser.add_argument("--fp16", action="store_true", help="Enable fp16 mixed precision training")
    parser.add_argument("--gradient_accumulation", type=int, default=1, help="Gradient accumulation steps")
    parser.add_argument("--max_input_length", type=int, default=16, help="Max length of input sequence")
    parser.add_argument("--max_output_length", type=int, default=8, help="Max length of target sequence")
    parser.add_argument("--model_name_or_path", type=str, default="google/flan-t5-small", help="Base model checkpoint")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("STARTING HUGGINGFACE FLAN-T5 TRAINING PIPELINE")
    print("=" * 80)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device detected: {device}")
    if device == "cuda":
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        
    print(f"Loading base model and tokenizer: {args.model_name_or_path}")
    tokenizer = T5TokenizerFast.from_pretrained(args.model_name_or_path)
    model = T5ForConditionalGeneration.from_pretrained(args.model_name_or_path)
    model.config.tie_word_embeddings = False
    
    # 1. Extract unique emojis from datasets to add to tokenizer
    unique_emojis = set()
    for path in [args.train_path, args.val_path]:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for item in data:
                        for em in item["output"].split():
                            unique_emojis.add(em)
                except Exception as e:
                    print(f"Warning reading {path}: {e}")
                    
    unique_emojis = sorted(list(unique_emojis))
    print(f"Found {len(unique_emojis)} unique emojis in dataset.")
    
    if len(unique_emojis) > 0:
        added = tokenizer.add_tokens(unique_emojis)
        print(f"Added {added} new emoji tokens to tokenizer. Total Vocab: {len(tokenizer)}")
        model.resize_token_embeddings(len(tokenizer))
        
        # Initialize new token embeddings with the embeddings of their English word counterparts
        print("Initializing new token embeddings semantically from base vocabulary...")
        temp_tokenizer = T5TokenizerFast.from_pretrained(args.model_name_or_path)
        with torch.no_grad():
            old_emb = model.shared.weight[:-added]
            mean_emb = old_emb.mean(dim=0)
            std_emb = old_emb.std(dim=0)
            
            # Start with mean + a tiny bit of noise
            new_weights = mean_emb + torch.randn(added, old_emb.size(1), device=old_emb.device) * std_emb * 0.1
            
            # For lm_head (if not tied)
            lm_weights = None
            if hasattr(model, "lm_head") and model.lm_head is not None and model.lm_head.weight is not model.shared.weight:
                old_lm = model.lm_head.weight[:-added]
                mean_lm = old_lm.mean(dim=0)
                std_lm = old_lm.std(dim=0)
                lm_weights = mean_lm + torch.randn(added, old_lm.size(1), device=old_lm.device) * std_lm * 0.1
            
            for i, emoji_token in enumerate(unique_emojis):
                # Clean token, e.g. [happy] -> happy, [rainy_day] -> rainy day
                cleaned = emoji_token.replace("[", "").replace("]", "").replace("_", " ").strip().lower()
                sub_ids = temp_tokenizer.encode(cleaned, add_special_tokens=False)
                
                # Filter out ids that are out of bounds of the old embedding
                sub_ids = [idx for idx in sub_ids if idx < len(old_emb)]
                
                if sub_ids:
                    # Get average of original subword embeddings
                    sub_weights = old_emb[sub_ids].mean(dim=0)
                    new_weights[i] = sub_weights
                    if lm_weights is not None:
                        lm_weights[i] = old_lm[sub_ids].mean(dim=0)
            
            # Assign
            model.shared.weight[-added:] = new_weights
            if lm_weights is not None:
                model.lm_head.weight[-added:] = lm_weights
        print("Semantic initialization of new token embeddings complete.")
            
    # 2. Configure PEFT / LoRA
    print("\n>>> Wrapping model with LoRA...")
    try:
        from peft import LoraConfig, get_peft_model, TaskType
        import inspect
        
        print("Type of model.shared before get_peft_model:", type(model.shared))
        print("Type of model.lm_head before get_peft_model:", type(model.lm_head))
        print("lm_head weight is shared weight:", model.lm_head.weight is model.shared.weight)
        print("Is encoder.embed_tokens model.shared?", model.encoder.embed_tokens is model.shared)
        print("Is decoder.embed_tokens model.shared?", model.decoder.embed_tokens is model.shared)
        print("Is encoder.embed_tokens model.lm_head?", model.encoder.embed_tokens is model.lm_head)
        
        peft_kwargs = {
            "task_type": TaskType.SEQ_2_SEQ_LM,
            "inference_mode": False,
            "r": 32,
            "lora_alpha": 64,
            "lora_dropout": 0.1,
            "target_modules": ["q", "v", "k", "o", "wi_0", "wi_1", "wo"],
            "modules_to_save": ["shared", "lm_head"], # Crucial: saves the newly learned token embeddings inside the LoRA adapter!
        }
        
        if "ensure_weight_tying" in inspect.signature(LoraConfig.__init__).parameters:
            peft_kwargs["ensure_weight_tying"] = False
            
        peft_config = LoraConfig(**peft_kwargs)
        model = get_peft_model(model, peft_config)
        
        # Manually ensure encoder/decoder embed_tokens point to the wrapped shared module
        model.encoder.embed_tokens = model.shared
        model.decoder.embed_tokens = model.shared
        
        print("Type of model.shared after get_peft_model:", type(model.shared))
        print("Type of model.lm_head after get_peft_model:", type(model.lm_head))
        print("Is encoder.embed_tokens model.shared?", model.encoder.embed_tokens is model.shared)
        print("Is decoder.embed_tokens model.shared?", model.decoder.embed_tokens is model.shared)
        print("Is encoder.embed_tokens model.lm_head?", model.encoder.embed_tokens is model.lm_head)
        
        if hasattr(model.shared, "modules_to_save"):
            print("model.shared modules_to_save['default'] type:", type(model.shared.modules_to_save['default']))
        if hasattr(model.lm_head, "modules_to_save"):
            print("model.lm_head modules_to_save['default'] type:", type(model.lm_head.modules_to_save['default']))
        if hasattr(model.encoder.embed_tokens, "modules_to_save"):
            print("model.encoder.embed_tokens modules_to_save['default'] type:", type(model.encoder.embed_tokens.modules_to_save['default']))
                
        model.print_trainable_parameters()
        print("LoRA configuration applied successfully.")
    except ImportError:
        print("Warning: PEFT library not installed. Continuing with full fine-tuning.")
            
    # Load dataset using datasets.load_dataset("json")
    print(f"Loading datasets via load_dataset('json')...")
    data_files = {"train": args.train_path, "validation": args.val_path}
    dataset = load_dataset("json", data_files=data_files)
    
    # Tokenization preprocessing function
    def preprocess_function(examples):
        model_inputs = tokenizer(
            examples["input"],
            max_length=args.max_input_length,
            padding="max_length",
            truncation=True
        )
        
        labels = tokenizer(
            text_target=examples["output"],
            max_length=args.max_output_length,
            padding="max_length",
            truncation=True
        )
        
        # Mask labels (-100 for pad tokens)
        label_ids = []
        for ids in labels["input_ids"]:
            clean_ids = [(idx if idx != tokenizer.pad_token_id else -100) for idx in ids]
            label_ids.append(clean_ids)
            
        model_inputs["labels"] = label_ids
        return model_inputs
        
    tokenized_datasets = dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=dataset["train"].column_names
    )
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    # Training Arguments: Optimize for GPU/CPU resources
    use_bf16 = False
    use_fp16 = False
    use_gradient_checkpointing = False
    optimizer_choice = "adamw_torch"
    
    if torch.cuda.is_available():
        use_gradient_checkpointing = True
        optimizer_choice = "adafactor"
        if torch.cuda.is_bf16_supported():
            use_bf16 = True
            print("GPU supports BF16 precision. Enabling BF16 training.")
        else:
            use_fp16 = True
            print("GPU does not support BF16. Enabling FP16 mixed precision.")
            
    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=0.05, # Increased weight decay for regularization
        save_total_limit=1,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        fp16=use_fp16,
        bf16=use_bf16,
        gradient_checkpointing=use_gradient_checkpointing,
        optim=optimizer_choice,
        max_grad_norm=1.0, # Add gradient clipping to prevent exploding gradients
        gradient_accumulation_steps=args.gradient_accumulation,
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss", # Changed from loss to eval_loss to prevent overfitting
        greater_is_better=False,
        report_to="none"
    )
    
    # Trainer
    test_callback = EpochInferenceCallback(model, tokenizer, device)
    
    import inspect
    trainer_kwargs = {
        "model": model,
        "args": training_args,
        "train_dataset": tokenized_datasets["train"],
        "eval_dataset": tokenized_datasets["validation"],
        "data_collator": data_collator,
        "callbacks": [test_callback]
    }
    sig = inspect.signature(Seq2SeqTrainer.__init__)
    if "processing_class" in sig.parameters:
        trainer_kwargs["processing_class"] = tokenizer
    else:
        trainer_kwargs["tokenizer"] = tokenizer

    trainer = Seq2SeqTrainer(**trainer_kwargs)
    
    # Train
    print("Training model...")
    trainer.train()
    
    # Save the best model and tokenizer
    print(f"Saving best model and tokenizer to: {args.output_dir}")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    
    print("\nTraining completed successfully!")
    print("=" * 80)

if __name__ == "__main__":
    main()
