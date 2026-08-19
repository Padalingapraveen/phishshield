import pandas as pd
from pathlib import Path

PREDICTIONS = Path(
    r"B:\PhishGuard-AI\results\inference_evaluation"
    r"\inference_predictions.csv"
)

OUTPUT = Path(
    r"B:\PhishGuard-AI\results\inference_evaluation"
    r"error_analysis.csv"
)

df = pd.read_csv(PREDICTIONS)

THRESHOLD = 0.47

df["predicted_label"] = (
    df["phishing_probability"] >= THRESHOLD
).astype(int)

df["error_type"] = "CORRECT"

df.loc[
    (df["label"] == 1) &
    (df["predicted_label"] == 0),
    "error_type"
] = "FALSE_NEGATIVE"

df.loc[
    (df["label"] == 0) &
    (df["predicted_label"] == 1),
    "error_type"
] = "FALSE_POSITIVE"

errors = df[df["error_type"] != "CORRECT"].copy()

print("=" * 70)
print("PHISHGUARD AI - ERROR ANALYSIS")
print("=" * 70)

print("\nTotal errors:", len(errors))

print("\nError distribution:")
print(errors["error_type"].value_counts())

print("\n" + "=" * 70)
print("FALSE NEGATIVES")
print("=" * 70)

fn = errors[
    errors["error_type"] == "FALSE_NEGATIVE"
].copy()

print(
    fn[
        [
            "index",
            "label",
            "predicted_label",
            "phishing_probability",
            "risk_score",
            "sender",
            "subject"
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 70)
print("FALSE POSITIVES")
print("=" * 70)

fp = errors[
    errors["error_type"] == "FALSE_POSITIVE"
].copy()

print(
    fp[
        [
            "index",
            "label",
            "predicted_label",
            "phishing_probability",
            "risk_score",
            "sender",
            "subject"
        ]
    ].to_string(index=False)
)

errors.to_csv(OUTPUT, index=False)

print("\nSaved:")
print(OUTPUT)