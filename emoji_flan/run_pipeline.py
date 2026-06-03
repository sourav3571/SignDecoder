import os
import sys
import argparse
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_HERE = os.path.dirname(os.path.abspath(__file__))

def run_command(cmd, desc):
    print(f"\n>>> Running: {desc}...")
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True, cwd=_HERE)
    if result.returncode != 0:
        print(f"Error occurred during: {desc}")
        sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser(description="End-to-end training pipeline.")
    parser.add_argument("--raw_dataset", type=str, default="word_emoji_dataset", help="Raw dataset name or path")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--output_dir", type=str, default="data", help="Output dir for processed data")
    parser.add_argument("--model_dir", type=str, default="models/flan_emoji", help="Output dir for model")
    parser.add_argument("--val_split", type=float, default=0.1, help="Validation split size")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--fp16", action="store_true", help="Use FP16 training")
    parser.add_argument("--model_name_or_path", type=str, default="google/flan-t5-small", help="Base model name or path")
    
    args = parser.parse_args()
    
    # 1. Preprocessing
    preprocess_cmd = [
        sys.executable,
        os.path.join("src", "preprocess.py"),
        "--raw_dataset", args.raw_dataset,
        "--output_dir", args.output_dir,
        "--val_split", str(args.val_split)
    ]
    run_command(preprocess_cmd, "Preprocessing Step")
    
    # 2. Training
    train_path = os.path.join(args.output_dir, "train.json")
    val_path = os.path.join(args.output_dir, "val.json")
    
    train_cmd = [
        sys.executable,
        os.path.join("src", "train.py"),
        "--train_path", train_path,
        "--val_path", val_path,
        "--epochs", str(args.epochs),
        "--batch_size", str(args.batch_size),
        "--lr", str(args.lr),
        "--output_dir", args.model_dir,
        "--model_name_or_path", args.model_name_or_path
    ]
    if args.fp16:
        train_cmd.append("--fp16")
        
    run_command(train_cmd, "Model Training Step")
    
    # 3. Copy to backend if backend exists
    backend_model_dir = os.path.abspath(os.path.join(_HERE, "..", "backend", "models", "emoji_ml"))
    if os.path.exists(backend_model_dir):
        print(f"\n>>> Copying trained model files to backend: {backend_model_dir}...")
        import shutil
        files_to_copy = [
            "adapter_config.json",
            "adapter_model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
            "special_tokens_map.json"
        ]
        for f_name in files_to_copy:
            src_f = os.path.join(args.model_dir, f_name)
            dst_f = os.path.join(backend_model_dir, f_name)
            if os.path.exists(src_f):
                shutil.copy2(src_f, dst_f)
                print(f"  Copied {f_name}")
            else:
                print(f"  Warning: {f_name} not found in output directory")

    # 4. Print Training Summary
    print("\n" + "=" * 50)
    print("PIPELINE TRAINING SUMMARY")
    print("=" * 50)
    print(f"Dataset Used:       {args.raw_dataset}")
    print(f"Processed Output:  {args.output_dir}/")
    print(f"Training Epochs:   {args.epochs}")
    print(f"Batch Size:        {args.batch_size}")
    print(f"Learning Rate:     {args.lr}")
    print(f"Model Saved To:    {args.model_dir}")
    print("=" * 50)
    print("Pipeline run completed successfully!")

if __name__ == "__main__":
    main()
