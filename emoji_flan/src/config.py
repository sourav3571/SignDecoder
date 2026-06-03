import os

# Base paths
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)

# Defaults
DEFAULT_MODEL_NAME = "google/flan-t5-base"
DEFAULT_RAW_DATASET = r"d:\Dataset\word_emoji_dataset.json"
DEFAULT_DATA_DIR = os.path.join(PROJECT_DIR, "data")
DEFAULT_MODEL_DIR = os.path.join(PROJECT_DIR, "models", "flan_emoji")

# Tokenizer options
MAX_INPUT_LENGTH = 64
MAX_OUTPUT_LENGTH = 32
