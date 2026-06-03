import os
import sys
import argparse
import torch
from transformers import T5ForConditionalGeneration, T5TokenizerFast

# Adjust path to import src.utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import map_emojis_to_words, map_words_to_emojis

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Inference script for FLAN-T5 Gloss-to-Emoji translation.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to fine-tuned model directory")
    parser.add_argument("--text", type=str, required=True, help="Text to translate into emoji")
    parser.add_argument("--max_length", type=int, default=32, help="Max output length for generation")
    parser.add_argument("--num_beams", type=int, default=4, help="Number of beams for search")
    parser.add_argument("--temperature", type=float, default=1.0, help="Temperature for generation")
    parser.add_argument("--top_p", type=float, default=0.9, help="Top-p for generation")
    parser.add_argument("--map_dict", action="store_true", help="Map generated emoji sequence back to text using dictionary")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model_path):
        print(f"Error: Model path '{args.model_path}' does not exist.")
        sys.exit(1)
        
    print(f"Loading tokenizer from: {args.model_path}")
    tokenizer = T5TokenizerFast.from_pretrained(args.model_path)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    adapter_config_path = os.path.join(args.model_path, "adapter_config.json")
    if os.path.exists(adapter_config_path):
        import json
        from peft import PeftModel
        base_model_name = "google/flan-t5-small"
        try:
            with open(adapter_config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                base_model_name = config_data.get("base_model_name_or_path", base_model_name)
        except Exception as e:
            print(f"Warning: Failed to read base model name from adapter config: {e}")
            
        print(f"Loading base model {base_model_name}...")
        base_model = T5ForConditionalGeneration.from_pretrained(base_model_name)
        
        # Resize token embeddings of base model to match expanded tokenizer
        base_model.resize_token_embeddings(len(tokenizer))
        
        print(f"Loading adapter weights from: {args.model_path}")
        model = PeftModel.from_pretrained(base_model, args.model_path)
    else:
        print(f"No adapter config found. Loading standard model weights...")
        model = T5ForConditionalGeneration.from_pretrained(args.model_path)
        
    model.to(device)
    model.eval()
    
    # Prepend task prompt prefix
    prompt = f"translate gloss to emoji: {args.text.strip().lower()}"
    print(f"Prompt: '{prompt}'")
    
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt", max_length=64, truncation=True).to(device)
    
    # Generate output sequence
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=args.max_length,
            num_beams=args.num_beams,
            temperature=args.temperature,
            top_p=args.top_p,
            do_sample=(args.temperature != 1.0 or args.top_p != 1.0)
        )
    
    # Decode outputs skipping special tokens
    predicted_labels = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    print(f"Raw Output Labels: '{predicted_labels}'")
    
    # Convert labels to actual emojis using the local dictionary helper
    emoji_seq = map_words_to_emojis(predicted_labels)
    print(f"Translated Emojis: '{emoji_seq}'")
    
    # Map back if requested
    if args.map_dict:
        mapped_tokens = map_emojis_to_words(emoji_seq)
        print(f"Mapped tokens: {mapped_tokens}")

if __name__ == "__main__":
    main()
