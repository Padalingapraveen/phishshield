# PhishGuard-AI

This project provides a phishing detection service built around a DistilBERT + GAT model pipeline.

## Project structure

- `api/` contains the FastAPI application and supporting modules.
- `models/distilbert_gat/deployment/` holds the trained model artifacts and tokenizer assets.
- `data/` is reserved for training and inference datasets.
- `results/` is reserved for experiment outputs and evaluation artifacts.

## Setup

1. Create a virtual environment.
2. Install dependencies from `requirements-api.txt`.
3. Run the API with:

```bash
uvicorn api.main:app --reload
```
