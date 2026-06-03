import os
from huggingface_hub import HfApi, login

def main():
    print("=" * 60)
    print("🤗 Hugging Face Model Upload Utility")
    print("=" * 60)
    
    # 1. Ask for credentials
    token = input("Please enter your Hugging Face API Token (with WRITE permission): ").strip()
    if not token:
        print("Error: API Token is required.")
        return
        
    try:
        login(token=token, add_to_git_credential=True)
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 2. Ask for repository name
    repo_name = input("Enter target repository name (e.g., 'flan-t5-emoji-translator'): ").strip()
    if not repo_name:
        print("Error: Repository name is required.")
        return
        
    repo_id = f"souravbehera3571/{repo_name}"
    
    # 3. Model directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_model_dir = os.path.join(project_root, "models", "flan_emoji")
    model_dir = input(f"Enter model directory to upload [Default: {default_model_dir}]: ").strip()
    if not model_dir:
        model_dir = default_model_dir
        
    if not os.path.exists(model_dir):
        # Resolve path relative to the project root directory
        cleaned_dir = model_dir.lstrip("/\\")
        # Try both the root level and under emoji_flan
        paths_to_try = [
            os.path.abspath(os.path.join(project_root, cleaned_dir)),
            os.path.abspath(os.path.join(project_root, "emoji_flan", cleaned_dir)),
            os.path.abspath(os.path.join(project_root, "..", cleaned_dir))
        ]
        for p in paths_to_try:
            if os.path.exists(p):
                model_dir = p
                break
                
    if not os.path.exists(model_dir):
        print(f"Error: Model directory '{model_dir}' does not exist.")
        return

    api = HfApi()
    
    # 4. Create repo if it doesn't exist
    print(f"\nCreating/Verifying repository: {repo_id}...")
    try:
        api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
        print("Repository is ready.")
    except Exception as e:
        print(f"Failed to create repository: {e}")
        return

    # 5. Upload folder
    print(f"Uploading files from '{model_dir}' to '{repo_id}'...")
    try:
        # Uploads all config and model adapter files while ignoring large optimizer states or checkpoints
        api.upload_folder(
            folder_path=model_dir,
            repo_id=repo_id,
            repo_type="model",
            ignore_patterns=["**/checkpoint-*", "**/optimizer.pt", "**/scheduler.pt"]
        )
        print("\n🎉 Upload completed successfully!")
        print(f"View your model at: https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"\nUpload failed: {e}")

if __name__ == "__main__":
    main()
