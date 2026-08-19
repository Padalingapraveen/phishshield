from pathlib import Path

from model import load_gat_model


MODEL_PATH = Path(
    "models/distilbert_gat/deployment/distilbert_gat_best.pt"
)


print("=" * 60)
print("PHISHGUARD AI - GAT MODEL VERIFICATION")
print("=" * 60)

model, checkpoint, device = load_gat_model(
    MODEL_PATH
)

print("\nModel loaded successfully.")

print("\nBest epoch:")
print(checkpoint["best_epoch"])

print("\nLabel mapping:")
print(checkpoint["label_mapping"])

print("\nTest metrics:")

for key, value in checkpoint["test_metrics"].items():

    print(
        f"{key}: {value}"
    )

print("\n✓ Exact trained GAT architecture loaded.")