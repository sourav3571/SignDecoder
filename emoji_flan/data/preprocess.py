import json

# Load your JSON file
with open('word_emoji_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"📂 Total entries loaded: {len(data)}")

# -----------------------------------------------
# Clean: Keep only word + emoji_sequence_text
# -----------------------------------------------
cleaned_data = []
skipped = 0

for entry in data:
    
    # Skip if required fields are missing
    if 'word' not in entry or 'emoji_sequence_text' not in entry:
        print(f"⚠️  Skipping entry - missing fields: {entry}")
        skipped += 1
        continue
    
    # Skip if emoji_sequence_text is empty
    if not entry['emoji_sequence_text']:
        print(f"⚠️  Skipping empty emoji sequence for word: {entry['word']}")
        skipped += 1
        continue

    # Tokenize input word/phrase into individual words
    input_tokens = entry['word'].lower().strip().split()
    
    # Output tokens (already a list in your JSON)
    output_tokens = [token.lower().strip() for token in entry['emoji_sequence_text']]
    
    cleaned_entry = {
        "input": entry['word'].lower().strip(),
        "output": entry['emoji_sequence_text'],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens
    }
    
    cleaned_data.append(cleaned_entry)

# -----------------------------------------------
# Save cleaned JSON
# -----------------------------------------------
with open('cleaned_word_emoji_dataset.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

# -----------------------------------------------
# Summary
# -----------------------------------------------
print(f"\n✅ Done!")
print(f"   Total loaded  : {len(data)}")
print(f"   Total cleaned : {len(cleaned_data)}")
print(f"   Total skipped : {skipped}")
print(f"\n💾 Saved to --> cleaned_word_emoji_dataset.json")

print(f"\n📋 First 3 Sample Entries:")
print("-" * 40)
for entry in cleaned_data[:3]:
    print(f"  INPUT TOKENS  : {entry['input_tokens']}")
    print(f"  OUTPUT TOKENS : {entry['output_tokens']}")
    print()