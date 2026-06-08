import os
import json
import argparse
from sklearn.model_selection import train_test_split

def main():
    parser = argparse.ArgumentParser(description="Preprocess word-emoji dataset.")
    parser.add_argument("--raw_dataset", type=str, default="emoji_flan/data/word_emoji_dataset.json", help="Path to raw dataset JSON")
    parser.add_argument("--output_dir", type=str, default="emoji_flan/data", help="Directory to save splits")
    parser.add_argument("--val_split", type=float, default=0.1, help="Validation split ratio")
    args = parser.parse_args()

    # Load Raw Dataset
    if not os.path.exists(args.raw_dataset):
        print(f"Error: Raw dataset not found at {args.raw_dataset}")
        return

    with open(args.raw_dataset, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    processed_pairs = []
    seen = set()
    for item in raw_data:
        # Support both 'word' (raw text) and 'text_emoji_sequence' (bracketed labels)
        word = item.get("word", "")
        if not word:
            word = item.get("input", "")
        word = word.strip().lower()

        cluster = item.get("cluster", "NEUTRAL")

        emoji_labels = item.get("text_emoji_sequence", "")
        if not emoji_labels and "output" in item:
            output_val = item["output"]
            if isinstance(output_val, list):
                emoji_labels = " ".join(f"[{x}]" for x in output_val)
            else:
                emoji_labels = str(output_val)
        emoji_labels = emoji_labels.strip()

        if not word or not emoji_labels:
            continue

        # Format prompt for FLAN-T5
        input_str = f"translate gloss to emoji: {word}"
        output_str = emoji_labels

        if input_str not in seen:
            seen.add(input_str)
            processed_pairs.append({
                "input": input_str,
                "output": output_str
            })

    print(f"Loaded {len(raw_data)} records. Cleaned to {len(processed_pairs)} unique pairs.")

    # Split into Train and Validation sets
    train_data, val_data = train_test_split(processed_pairs, test_size=args.val_split, random_state=42)
    print(f"Split size: {len(train_data)} train, {len(val_data)} validation")

    # Save to output directory
    os.makedirs(args.output_dir, exist_ok=True)
    for name, data in [("train.json", train_data), ("val.json", val_data)]:
        path = os.path.join(args.output_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {path}")

if __name__ == "__main__":
    main()
