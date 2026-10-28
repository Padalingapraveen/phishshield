import os
from pathlib import Path

# Load basic .env if present (we avoid adding a python-dotenv dependency if it's not present)
env_path = Path(".env")
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path("models/distilbert_gat/deployment")

MODEL_PATH = Path(os.getenv(
    "MODEL_PATH",
    str(BASE_DIR / "distilbert_gat_best.pt")
))

GRAPH_PATH = Path(os.getenv(
    "GRAPH_PATH",
    str(BASE_DIR / "graph_data.pt")
))

EMBEDDINGS_PATH = Path(os.getenv(
    "EMBEDDINGS_PATH",
    str(BASE_DIR / "train_embeddings.pt")
))

REFERENCE_PATH = Path(os.getenv(
    "REFERENCE_PATH",
    str(BASE_DIR / "reference_emails.csv")
))

TOKENIZER_PATH = Path(os.getenv(
    "TOKENIZER_PATH",
    str(BASE_DIR / "tokenizer")
))

# ============================================================
# PRODUCTION CONFIGURATION
# ============================================================

CLASSIFICATION_THRESHOLD = float(os.getenv("CLASSIFICATION_THRESHOLD", "0.47"))

# ============================================================
# RISK LEVEL CONFIGURATION
# ============================================================

RISK_MEDIUM_THRESHOLD = float(os.getenv("RISK_MEDIUM_THRESHOLD", "0.47"))
RISK_HIGH_THRESHOLD = float(os.getenv("RISK_HIGH_THRESHOLD", "0.60"))
RISK_CRITICAL_THRESHOLD = float(os.getenv("RISK_CRITICAL_THRESHOLD", "0.80"))

# ============================================================
# API CONFIGURATION
# ============================================================

# Note: For Chrome Extensions, use the chrome-extension://<EXTENSION_ID> origin
# If the extension is loaded unpacked, the ID is dynamic. You MUST add your dynamically
# generated ID to the .env file like this:
# CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,chrome-extension://abcdefghijklmnop
_cors_env = os.getenv("CORS_ORIGINS", "")
if not _cors_env and os.getenv("ENVIRONMENT", "development") != "production":
    _cors_env = "http://localhost:5173,http://127.0.0.1:5173"

CORS_ORIGINS = [origin.strip() for origin in _cors_env.split(",") if origin.strip()]

# ============================================================
# RATE LIMITING CONFIGURATION
# ============================================================

RATE_LIMIT_LOGIN = os.getenv("RATE_LIMIT_LOGIN", "5/minute")
RATE_LIMIT_REGISTER = os.getenv("RATE_LIMIT_REGISTER", "3/minute")
RATE_LIMIT_PREDICT = os.getenv("RATE_LIMIT_PREDICT", "100/minute")

# ============================================================
# SECURITY CONFIGURATION
# ============================================================
COOKIE_SECURE = os.getenv("ENVIRONMENT", "development") == "production"
