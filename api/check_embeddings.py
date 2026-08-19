import torch
from pathlib import Path

PATH = Path(
    "models/distilbert_gat/deployment/train_embeddings.pt"
)

print("=" * 60)
print("PHISHGUARD AI - EMBEDDING CHECK")
print("=" * 60)

embeddings = torch.load(
    PATH,
    map_location="cpu",
    weights_only=False
)

print("Type:")
print(type(embeddings))

print("\nShape:")
print(embeddings.shape)

print("\nData type:")
print(embeddings.dtype)

print("\nExpected:")
print("(23492, 768)")