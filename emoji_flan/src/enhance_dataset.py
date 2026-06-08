import os
import json
import argparse
from clustering import SemanticClusteringEngine

def main():
    parser = argparse.ArgumentParser(description="Enhance dataset with semantic clustering field.")
    parser.add_argument("--dataset_path", type=str, default="emoji_flan/data/cleaned_word_emoji_dataset.json", help="Path to raw or cleaned dataset JSON")
    args = parser.parse_args()

    if not os.path.exists(args.dataset_path):
        print(f"Error: Dataset file not found at {args.dataset_path}")
        return

    print(f"Loading dataset from {args.dataset_path}...")
    with open(args.dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Enhancing {len(data)} entries with semantic clusters...")
    engine = SemanticClusteringEngine()

    cluster_counts = {}
    for entry in data:
        # Get input word/phrase
        input_text = entry.get("input", entry.get("word", ""))
        # Classify using clustering engine
        cluster = engine.classify(input_text)
        # Append "cluster" field, leaving other fields untouched
        entry["cluster"] = cluster
        
        # Track counts
        cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1

    print("\nClustering distribution:")
    for cluster, count in sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cluster}: {count} ({count/len(data)*100:.2f}%)")

    # Save the enhanced dataset back to the same file
    with open(args.dataset_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nSuccessfully enhanced and saved dataset to {args.dataset_path}")

if __name__ == "__main__":
    main()
