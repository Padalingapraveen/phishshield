# PhishGuard AI

Enterprise phishing detection platform powered by a **DistilBERT + Graph Attention Network (GAT)** model pipeline. Consists of three components:

- **`api/`** – FastAPI backend (REST API, JWT auth, SQLite DB)
- **`frontend/`** – React/Vite dashboard (SOC monitoring, analytics)
- **`extension/`** – Chrome extension (real-time Gmail / webmail scanning)

---

## Model Performance

Evaluated on the **CEAS-08** dataset at threshold **0.47**:

| Metric     | Test Set | Inference Snapshot |
|------------|----------|--------------------|
| Accuracy   | 97.05%   | 98.25%             |
| Precision  | 97.11%   | 97.35%             |
| Recall     | 97.62%   | 99.20%             |
| F1 Score   | 97.36%   | 98.27%             |
| ROC AUC    | 99.70%   | 99.88%             |

---

## Project Structure

```
PhishGuard-AI/
├── api/                          # FastAPI backend
│   ├── __init__.py
│   ├── main.py                   # App entry-point & all routes
│   ├── auth.py                   # JWT authentication
│   ├── config.py                 # Environment-based config
│   ├── database.py               # SQLAlchemy setup & init
│   ├── embedding.py              # DistilBERT embedder
│   ├── graph.py                  # Reference graph builder
│   ├── model.py                  # GAT model loader
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── performance_service.py    # Analytics & chart service
│   ├── predictor.py              # End-to-end inference pipeline
│   ├── preprocessing.py          # Email preprocessing
│   └── schemas.py                # Pydantic request/response schemas
├── frontend/                     # React + Vite dashboard
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── styles.css
│       ├── context/AuthContext.jsx
│       ├── services/api.js
│       ├── components/
│       │   ├── dashboard/        # Dashboard widgets
│       │   └── layout/           # Sidebar, Topbar, Layout
│       └── pages/                # All page components
├── extension/                    # Chrome Extension (MV3)
│   ├── manifest.json
│   ├── background/api_client.js
│   ├── content/
│   │   ├── content.js
│   │   └── extractors/
│   │       ├── gmail.js
│   │       └── generic.js
│   └── popup/
│       ├── popup.html
│       ├── popup.js
│       └── popup.css
├── models/                       # Trained model artifacts (use Git LFS)
│   └── distilbert_gat/deployment/
│       ├── distilbert_gat_best.pt   # GAT model weights (~2.5 MB)
│       ├── graph_data.pt            # Reference graph (~10.5 MB)
│       ├── train_embeddings.pt      # Training embeddings (~69 MB)
│       ├── reference_emails.csv     # Reference email corpus (~76 MB)
│       ├── model_config.json
│       └── tokenizer/
│           ├── config.json
│           ├── model_metadata.json
│           ├── tokenizer.json
│           └── tokenizer_config.json
├── data/
│   ├── database/                 # Runtime DB directory (empty on clone)
│   └── processed/                # Processed datasets (gitignored)
├── tests/                        # Python test suite
├── requirements-api.txt          # Python dependencies
├── .env.example                  # Environment template → copy to .env
├── .gitignore
└── README.md
```

---

## Setup & Running

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git LFS (for large model files — see below)

### 1. Clone & Model Files

```bash
git clone https://github.com/YOUR_USERNAME/PhishGuard-AI.git
cd PhishGuard-AI
```

> **Large model files** (`*.pt`, `reference_emails.csv`) are tracked with **Git LFS**.
> Make sure Git LFS is installed: `git lfs install` then `git lfs pull`.

### 2. Backend (FastAPI)

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements-api.txt

# Configure environment
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
# Edit .env and set JWT_SECRET_KEY to a secure random string

# Initialize the database (creates admin user: admin / adminpassword)
python -c "from api.database import init_database; init_database()"

# Start the API server (http://127.0.0.1:8000)
uvicorn api.main:app --reload
```

### 3. Frontend (React/Vite)

```bash
cd frontend
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux

npm install
npm run dev                     # http://localhost:5173
```

### 4. Chrome Extension

1. Open Chrome → `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `extension/` folder
4. Copy the Extension ID shown → add it to your root `.env`:
   ```
   CORS_ORIGINS=http://localhost:5173,...,chrome-extension://YOUR_EXTENSION_ID
   ```
5. Restart the API server

---

## Running Tests

```bash
# Activate your virtual environment first
pytest tests/
```

---

## Git LFS Setup (for model files)

The large binary model files are stored in Git LFS. To track them:

```bash
git lfs install
git lfs track "models/**/*.pt"
git lfs track "models/**/*.csv"
git add .gitattributes
```

---

## Default Credentials

| Role  | Username | Password      |
|-------|----------|---------------|
| Admin | admin    | adminpassword |

> ⚠️ **Change the admin password and `JWT_SECRET_KEY` before any production deployment.**
