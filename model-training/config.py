from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data" / "processed"
TRAIN_FILE = DATA_DIR / "train.json"
VAL_FILE = DATA_DIR / "validation.json"
TEST_FILE = DATA_DIR / "test.json"

# Model paths
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)
MODEL_OUTPUT_DIR = MODELS_DIR / "bug-fix-model"

# Model configuration
MODEL_NAME = "Salesforce/codet5-base"  # Pre-trained CodeT5
MAX_INPUT_LENGTH = 512   # Max tokens for buggy code
MAX_TARGET_LENGTH = 512  # Max tokens for fixed code

# Training hyperparameters
BATCH_SIZE = 4           # Small batch for GPU memory
LEARNING_RATE = 5e-5     # Standard for fine-tuning
NUM_EPOCHS = 10          # Number of training passes
WARMUP_STEPS = 100       # Gradual learning rate increase
SAVE_STEPS = 100         # Save checkpoint every N steps
EVAL_STEPS = 100         # Evaluate every N steps
LOGGING_STEPS = 50       # Log metrics every N steps

# Early stopping
EARLY_STOPPING_PATIENCE = 3  # Stop if no improvement for 3 evals

# Device
DEVICE = "cuda"  # Use GPU (you have NVIDIA)