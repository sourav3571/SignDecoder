# FLAN-T5 Emoji Translation Pipeline

This directory contains a complete, production-ready, terminal-based ML pipeline for training and using a fine-tuned `google/flan-t5-base` model to translate English text/gloss sequences into bracketed label sequences (e.g., `[rain] [day]`), which map directly to emojis via the application's registry.

## Project Structure

```text
emoji_flan/
├── data/                    # Generated train.json and val.json datasets
├── models/                  # Fine-tuned model checkpoints
├── src/
│   ├── config.py            # Configuration defaults
│   ├── preprocess.py        # Dataset preprocessing and validation split
│   ├── train.py             # Seq2Seq Trainer fine-tuning script
│   ├── inference.py         # Terminal-based model inference script
│   └── utils.py             # Emoji to text dictionary mapping utilities
├── run_pipeline.py          # Orchestration pipeline runner
├── requirements.txt         # Package dependencies
└── README.md                # Documentation (this file)
```

## Requirements & Setup

Make sure you have Python 3.10+ installed.

1. Navigate to the pipeline directory:
   ```bash
   cd d:\SignDecoder\emoji_flan
   ```

2. Install the package dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step-by-Step CLI Usage

### Step 1: Data Preprocessing

Preprocesses a raw dataset JSON file, identifies the correct text and emoji fields dynamically, cleans whitespaces, space-separates all emojis, removes duplicate entries, and splits the data into `train.json` and `val.json` sets.

```bash
python src/preprocess.py \
  --raw_dataset d:\Dataset\word_emoji_dataset.json \
  --output_dir data \
  --val_split 0.1
```

- `--raw_dataset`: Path to the raw JSON file (or name).
- `--output_dir`: Location to save the train and validation splits (default: `data`).
- `--val_split`: Float representing percentage for validation split (default: `0.1`).
- `--max_samples` (optional): Cap the dataset size for testing.

### Step 2: Model Training

Uses HuggingFace's Trainer API to fine-tune `google/flan-t5-base`. The script automatically identifies and adds emojis as new tokens in the tokenizer, resizes the model's token embeddings, masks the padding labels with `-100`, evaluations on validation set per epoch, and checkpoints the best model.

```bash
python src/train.py \
  --train_path data/train.json \
  --val_path data/val.json \
  --epochs 5 \
  --batch_size 8 \
  --lr 5e-5 \
  --output_dir models/flan_emoji \
  --fp16
```

- `--train_path`: Path to `train.json` (default: `data/train.json`).
- `--val_path`: Path to `val.json` (default: `data/val.json`).
- `--epochs`: Number of training epochs (default: `5`).
- `--batch_size`: Batch size per device (default: `8`).
- `--lr`: Learning rate (default: `5e-5`).
- `--output_dir`: Directory to save the final fine-tuned model (default: `models/flan_emoji`).
- `--fp16` (flag): Set to enable mixed-precision training if running on compatible NVIDIA GPUs.

### Step 3: Inference

Run predictions from the terminal using the fine-tuned model.

```bash
python src/inference.py \
  --model_path models/flan_emoji \
  --text "I love pizza"
```

To enable emoji-to-text mapping back using the local dictionary in `src/utils.py`, add the `--map_dict` flag:
```bash
python src/inference.py \
  --model_path models/flan_emoji \
  --text "I love pizza" \
  --map_dict
```

- `--model_path`: Path to the folder containing the saved checkpoint.
- `--text`: The English phrase or gloss sequence to translate.
- `--max_length`: Maximum generation output length (default: `32`).
- `--num_beams`: Number of beams for beam search (default: `4`).
- `--temperature`: Temperature for sampling (default: `1.0`).
- `--top_p`: Nucleus sampling top_p threshold (default: `0.9`).
- `--map_dict` (flag): Translates emojis back to text glosses using the vocabulary map defined in `src/utils.py`.

---

## Orchestrated Pipeline Execution

You can run the end-to-end preprocessing and training pipeline with a single command using `run_pipeline.py`:

```bash
python run_pipeline.py \
  --raw_dataset d:\Dataset\word_emoji_dataset.json \
  --epochs 5 \
  --batch_size 8
```

The script will:
1. Run `src/preprocess.py` to prepare train/validation splits.
2. Run `src/train.py` using the generated datasets.
3. Print a pipeline execution summary on terminal completion.
