import os
import json
import logging
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)

# Try importing sentence_transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class SemanticProjectionNet(nn.Module):
    """
    Learned projection network that maps raw sentence embeddings 
    to a shared semantic space where correct input-output pairs are aligned.
    """
    def __init__(self, embedding_dim=384, projection_dim=384):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embedding_dim, projection_dim),
            nn.LayerNorm(projection_dim),
            nn.ReLU(),
            nn.Linear(projection_dim, projection_dim)
        )
        
    def forward(self, x):
        return self.net(x)

class SemanticClusteringEngine:
    """
    Embedding-Driven Semantic Learning Engine.
    Replaces the previous rule-based clustering engine.
    Uses natural embedding proximity (k-NN) to discover neighborhoods dynamically.
    """
    def __init__(self, model_dir=None, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Determine model path
        if model_dir is None:
            _HERE = os.path.dirname(os.path.abspath(__file__))
            # Default to sibling models/ directory
            self.model_dir = os.path.abspath(os.path.join(_HERE, "..", "models"))
        else:
            self.model_dir = model_dir
            
        self.projection_path = os.path.join(self.model_dir, "semantic_projection.pt")
        self.embeddings_path = os.path.join(self.model_dir, "learned_embeddings.pt")
        
        # Load SentenceTransformer
        if HAS_SENTENCE_TRANSFORMERS:
            logger.info("Loading sentence-transformers/all-MiniLM-L6-v2...")
            self.emb_model = SentenceTransformer("all-MiniLM-L6-v2", device=self.device)
        else:
            logger.error("SentenceTransformers library not found!")
            self.emb_model = None
            
        # Initialize Projection Net
        self.projection_net = SemanticProjectionNet().to(self.device)
        self.projection_net.eval()
        
        # Data store
        self.inputs = []
        self.outputs = []
        self.projected_embeddings = None
        self.output_embeddings = None
        
        self.is_trained = self.load_model()
        if not self.is_trained:
            # Automatically try to train if training dataset is available
            _HERE = os.path.dirname(os.path.abspath(__file__))
            dataset_path = os.path.abspath(os.path.join(_HERE, "..", "data", "cleaned_word_emoji_dataset.json"))
            if os.path.exists(dataset_path):
                logger.info(f"Auto-training projection model using dataset at {dataset_path}...")
                success = train_embedding_alignment(dataset_path, self.model_dir, device=self.device)
                if success:
                    self.is_trained = self.load_model()
            else:
                logger.warning(f"Could not find dataset at {dataset_path} for auto-training.")
        
    def load_model(self) -> bool:
        if not os.path.exists(self.projection_path) or not os.path.exists(self.embeddings_path):
            logger.warning("Projection model or learned embeddings not found. The model needs to be trained.")
            return False
            
        try:
            # Load projection weights
            self.projection_net.load_state_dict(torch.load(self.projection_path, map_location=self.device))
            self.projection_net.eval()
            
            # Load precomputed embeddings
            data = torch.load(self.embeddings_path, map_location=self.device)
            self.inputs = data["inputs"]
            self.outputs = data["outputs"]
            self.projected_embeddings = data["projected_embeddings"].to(self.device)
            self.output_embeddings = data["output_embeddings"].to(self.device)
            
            logger.info(f"Loaded projection network and {len(self.inputs)} learned embeddings successfully.")
            return True
        except Exception as e:
            logger.error(f"Error loading model weights: {e}")
            return False

    def get_nearest_neighbors(self, text: str, k: int = 5) -> dict:
        """
        Retrieves the k-nearest neighbors using cosine similarity of projected embeddings.
        """
        if not self.is_trained or self.emb_model is None or self.projected_embeddings is None:
            # Return fallback default values
            return {
                "neighbors": [],
                "similarities": [],
                "semantic_cluster": "NEUTRAL",
                "cluster_confidence": 0.5,
                "closest_output": ""
            }
            
        # 1. Clean query
        query_text = str(text).strip().lower()
        if not query_text:
            return {
                "neighbors": [],
                "similarities": [],
                "semantic_cluster": "NEUTRAL",
                "cluster_confidence": 1.0,
                "closest_output": ""
            }
            
        # Strip prompt prefix if present
        prefix = "translate gloss to emoji:"
        if query_text.startswith(prefix):
            query_text = query_text[len(prefix):].strip()
            
        # 2. Embed query
        query_emb = self.emb_model.encode(query_text, convert_to_tensor=True, device=self.device)
        
        # 3. Project query
        with torch.no_grad():
            query_proj = self.projection_net(query_emb.unsqueeze(0))
            query_proj = F.normalize(query_proj, p=2, dim=-1)
            
        # 4. Compute cosine similarities
        similarities = torch.matmul(self.projected_embeddings, query_proj.t()).squeeze(-1) # shape: (N,)
        
        # 5. Retrieve top K
        actual_k = min(k, len(self.inputs))
        top_k_values, top_k_indices = torch.topk(similarities, k=actual_k)
        
        neighbors = [self.inputs[idx] for idx in top_k_indices.tolist()]
        sim_scores = top_k_values.tolist()
        closest_outputs = [self.outputs[idx] for idx in top_k_indices.tolist()]
        
        # Identify dominant semantic neighborhood (unique inputs joined by /)
        unique_neighbors = []
        for n in neighbors:
            if n not in unique_neighbors:
                unique_neighbors.append(n)
            if len(unique_neighbors) >= 3:
                break
        
        semantic_cluster = " / ".join(unique_neighbors).upper()
        cluster_confidence = round(sum(sim_scores) / len(sim_scores), 3) if sim_scores else 0.5
        
        return {
            "neighbors": neighbors,
            "similarities": sim_scores,
            "semantic_cluster": semantic_cluster,
            "cluster_confidence": cluster_confidence,
            "closest_output": closest_outputs[0] if closest_outputs else ""
        }

    def classify(self, text: str) -> str:
        """
        Classifies input text by returning the dynamic semantic neighborhood representation.
        """
        res = self.get_nearest_neighbors(text, k=3)
        return res["semantic_cluster"]


def train_embedding_alignment(dataset_path, save_dir, epochs=15, batch_size=128, lr=1e-3, device="cpu"):
    """
    Trains the projection model using contrastive InfoNCE loss to align input and output spaces.
    """
    print("=" * 80)
    print("TRAINING EMBEDDING PROXIMITY MODEL (FROM SCRATCH)")
    print("=" * 80)
    
    if not HAS_SENTENCE_TRANSFORMERS:
        print("Error: sentence-transformers is required for training.")
        return False
        
    os.makedirs(save_dir, exist_ok=True)
    
    # Load dataset
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return False
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} dataset records.")
    
    # Prepare inputs and outputs
    inputs = []
    outputs = []
    seen = set()
    for item in data:
        inp = item.get("input", "").strip().lower()
        # Clean any FLAN task prefix in dataset if present
        prefix = "translate gloss to emoji:"
        if inp.startswith(prefix):
            inp = inp[len(prefix):].strip()
            
        if not inp:
            continue
            
        # Format output
        out_val = item.get("output", "")
        if isinstance(out_val, list):
            out = " ".join(out_val)
        else:
            out = str(out_val)
        out = out.strip().lower()
        
        # Avoid duplicate pairs
        pair_key = (inp, out)
        if pair_key not in seen:
            seen.add(pair_key)
            inputs.append(inp)
            outputs.append(out)
            
    print(f"Cleaned dataset to {len(inputs)} unique input-output pairs.")
    
    # Load embedding model
    print("Loading SentenceTransformer model...")
    emb_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    
    # Encode inputs and outputs
    print("Generating dense semantic vectors...")
    input_embs = emb_model.encode(inputs, show_progress_bar=True, convert_to_tensor=True, device=device)
    output_embs = emb_model.encode(outputs, show_progress_bar=True, convert_to_tensor=True, device=device)
    
    # Set up projection net and optimizer
    projection_net = SemanticProjectionNet().to(device)
    projection_net.train()
    
    optimizer = torch.optim.AdamW(projection_net.parameters(), lr=lr, weight_decay=1e-4)
    
    # Training Loop
    dataset_size = len(inputs)
    print(f"Training for {epochs} epochs with batch size {batch_size}...")
    
    for epoch in range(epochs):
        indices = torch.randperm(dataset_size)
        epoch_loss = 0.0
        batches = 0
        
        for start_idx in range(0, dataset_size, batch_size):
            end_idx = min(start_idx + batch_size, dataset_size)
            batch_indices = indices[start_idx:end_idx]
            
            batch_x = input_embs[batch_indices]
            batch_y = output_embs[batch_indices]
            
            # Project inputs
            proj_x = projection_net(batch_x)
            
            # Normalize
            proj_x_norm = F.normalize(proj_x, p=2, dim=-1)
            batch_y_norm = F.normalize(batch_y, p=2, dim=-1)
            
            # Cosine similarity matrix: (B, B)
            sims = torch.matmul(proj_x_norm, batch_y_norm.t())
            
            # InfoNCE Loss
            B = proj_x.size(0)
            targets = torch.arange(B, device=device)
            temp = 0.07
            
            loss_i2o = F.cross_entropy(sims / temp, targets)
            loss_o2i = F.cross_entropy(sims.t() / temp, targets)
            loss = (loss_i2o + loss_o2i) / 2.0
            
            # Optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            batches += 1
            
        mean_loss = epoch_loss / batches
        print(f"  Epoch {epoch+1}/{epochs} - Loss: {mean_loss:.4f}")
        
    # Precompute all projected embeddings
    projection_net.eval()
    print("Precomputing all projected embeddings...")
    with torch.no_grad():
        projected_embeddings = []
        for start_idx in range(0, dataset_size, batch_size):
            end_idx = min(start_idx + batch_size, dataset_size)
            batch_x = input_embs[start_idx:end_idx]
            proj_x = projection_net(batch_x)
            proj_x_norm = F.normalize(proj_x, p=2, dim=-1)
            projected_embeddings.append(proj_x_norm)
        projected_embeddings = torch.cat(projected_embeddings, dim=0)
        
    # Save files
    projection_path = os.path.join(save_dir, "semantic_projection.pt")
    embeddings_path = os.path.join(save_dir, "learned_embeddings.pt")
    
    torch.save(projection_net.state_dict(), projection_path)
    torch.save({
        "inputs": inputs,
        "outputs": outputs,
        "projected_embeddings": projected_embeddings.cpu(),
        "output_embeddings": output_embs.cpu()
    }, embeddings_path)
    
    print(f"Model saved to {projection_path}")
    print(f"Embeddings saved to {embeddings_path}")
    print("Training finished successfully!\n")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train or test Semantic Embedding Proximity Model.")
    parser.add_argument("--dataset_path", type=str, default="emoji_flan/data/cleaned_word_emoji_dataset.json", help="Path to cleaned dataset JSON")
    parser.add_argument("--save_dir", type=str, default="emoji_flan/models", help="Directory to save model weights")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=128, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    args = parser.parse_args()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Train
    train_embedding_alignment(
        dataset_path=args.dataset_path,
        save_dir=args.save_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device=device
    )
    
    # Test
    print("Testing dynamic clustering inference...")
    engine = SemanticClusteringEngine(model_dir=args.save_dir, device=device)
    test_words = ["cheers", "grief", "joy", "grieving", "delighted", "rainy day"]
    for w in test_words:
        res = engine.get_nearest_neighbors(w, k=3)
        print(f"Input: '{w}'")
        print(f"  Neighborhood: {res['semantic_cluster']}")
        print(f"  Confidence  : {res['cluster_confidence']}")
        print(f"  Closest Out : {res['closest_output']}")
