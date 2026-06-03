import os
import sys
import traceback
import json
import torch
from datasets import Dataset
from transformers import (
    T5ForConditionalGeneration,
    T5TokenizerFast,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, TaskType

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"))

model_name_or_path = "google/flan-t5-base"
print("Loading model and tokenizer...")
tokenizer = T5TokenizerFast.from_pretrained(model_name_or_path)
model = T5ForConditionalGeneration.from_pretrained(model_name_or_path)

# Dummy dataset
train_data = [
    {"input": "translate gloss to emoji: happy today", "output": "[happy] [today]"},
    {"input": "translate gloss to emoji: rainy day", "output": "[rain] [day]"}
] * 8

# Resize token embeddings
added = tokenizer.add_tokens(["[happy]", "[today]", "[rain]", "[day]"])
model.resize_token_embeddings(len(tokenizer))

# Initialize new token embeddings
with torch.no_grad():
    old_emb = model.shared.weight[:-added]
    mean_emb = old_emb.mean(dim=0)
    std_emb = old_emb.std(dim=0)
    model.shared.weight[-added:] = mean_emb + torch.randn(added, old_emb.size(1)) * std_emb

print("Wrapping model with LoRA...")
peft_kwargs = {
    "task_type": TaskType.SEQ_2_SEQ_LM,
    "inference_mode": False,
    "r": 8,
    "lora_alpha": 32,
    "lora_dropout": 0.1,
    "target_modules": ["q", "v"],
    "modules_to_save": ["shared", "lm_head"],
}
peft_config = LoraConfig(**peft_kwargs)
model = get_peft_model(model, peft_config)

# Prepare dataset
dataset = Dataset.from_list(train_data)

def preprocess_function(examples):
    model_inputs = tokenizer(
        examples["input"],
        max_length=64,
        padding="max_length",
        truncation=True
    )
    labels = tokenizer(
        text_target=examples["output"],
        max_length=32,
        padding="max_length",
        truncation=True
    )
    label_ids = []
    for ids in labels["input_ids"]:
        clean_ids = [(idx if idx != tokenizer.pad_token_id else -100) for idx in ids]
        label_ids.append(clean_ids)
    model_inputs["labels"] = label_ids
    return model_inputs

tokenized_dataset = dataset.map(preprocess_function, batched=True)
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

training_args = Seq2SeqTrainingArguments(
    output_dir="./test_output",
    num_train_epochs=1,
    per_device_train_batch_size=8,
    learning_rate=3e-4,
    fp16=False,
    report_to="none"
)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
    processing_class=tokenizer
)

print("Starting training...")
try:
    trainer.train()
    print("Training finished successfully!")
except Exception as e:
    print("Caught exception during training:")
    traceback.print_exc()
