from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "results"
    / "inference_evaluation"
    / "inference_predictions.csv"
)


# ============================================================
# LOAD RESULTS
# ============================================================

print("=" * 70)
print("PHISHGUARD AI - THRESHOLD ANALYSIS")
print("=" * 70)

df = pd.read_csv(
    PREDICTIONS_PATH
)

print(
    f"\nLoaded predictions: {len(df)}"
)

print(
    "\nOriginal columns:"
)

print(
    list(df.columns)
)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = [
    "true_label",
    "phishing_probability"
]

missing = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing:

    raise RuntimeError(
        f"Missing required columns: {missing}"
    )


# ============================================================
# PREPARE DATA
# ============================================================

y_true = (
    df["true_label"]
    .astype(int)
    .values
)

probabilities = (
    df["phishing_probability"]
    .astype(float)
    .values
)


# ============================================================
# THRESHOLD EVALUATION
# ============================================================

thresholds = [
    0.30,
    0.35,
    0.40,
    0.42,
    0.44,
    0.45,
    0.46,
    0.47,
    0.48,
    0.49,
    0.50,
    0.51,
    0.52,
    0.53,
    0.54,
    0.55,
    0.56,
    0.58,
    0.60
]


results = []


print("\n")
print("=" * 70)
print("THRESHOLD COMPARISON")
print("=" * 70)

print(
    "\n"
    "Threshold | Accuracy | Precision | Recall | F1 | "
    "FP | FN"
)

print("-" * 70)


for threshold in thresholds:

    y_pred = (
        probabilities >= threshold
    ).astype(int)

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    )

    tn, fp, fn, tp = cm.ravel()

    results.append(
        {
            "threshold": threshold,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        }
    )

    print(
        f"{threshold:9.2f} | "
        f"{accuracy:8.4f} | "
        f"{precision:9.4f} | "
        f"{recall:6.4f} | "
        f"{f1:6.4f} | "
        f"{fp:3d} | "
        f"{fn:3d}"
    )


# ============================================================
# SAVE THRESHOLD RESULTS
# ============================================================

threshold_df = pd.DataFrame(
    results
)

output_path = (
    PROJECT_ROOT
    / "results"
    / "inference_evaluation"
    / "threshold_analysis.csv"
)

threshold_df.to_csv(
    output_path,
    index=False
)


# ============================================================
# BEST F1
# ============================================================

best_f1 = (
    threshold_df
    .loc[
        threshold_df["f1"].idxmax()
    ]
)


# ============================================================
# BEST RECALL
# ============================================================

best_recall = (
    threshold_df
    .loc[
        threshold_df["recall"].idxmax()
    ]
)


# ============================================================
# PRINT BEST RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("BEST F1 THRESHOLD")
print("=" * 70)

print(
    f"Threshold : "
    f"{best_f1['threshold']:.2f}"
)

print(
    f"Accuracy  : "
    f"{best_f1['accuracy']:.6f}"
)

print(
    f"Precision : "
    f"{best_f1['precision']:.6f}"
)

print(
    f"Recall    : "
    f"{best_f1['recall']:.6f}"
)

print(
    f"F1        : "
    f"{best_f1['f1']:.6f}"
)

print(
    f"FP        : "
    f"{int(best_f1['fp'])}"
)

print(
    f"FN        : "
    f"{int(best_f1['fn'])}"
)


print("\n")
print("=" * 70)
print("BEST RECALL THRESHOLD")
print("=" * 70)

print(
    f"Threshold : "
    f"{best_recall['threshold']:.2f}"
)

print(
    f"Accuracy  : "
    f"{best_recall['accuracy']:.6f}"
)

print(
    f"Precision : "
    f"{best_recall['precision']:.6f}"
)

print(
    f"Recall    : "
    f"{best_recall['recall']:.6f}"
)

print(
    f"F1        : "
    f"{best_recall['f1']:.6f}"
)

print(
    f"FP        : "
    f"{int(best_recall['fp'])}"
)

print(
    f"FN        : "
    f"{int(best_recall['fn'])}"
)


# ============================================================
# FALSE NEGATIVE ANALYSIS
# ============================================================

false_negatives = df[
    (
        df["true_label"] == 1
    )
    &
    (
        df["phishing_probability"] < 0.50
    )
].copy()


print("\n")
print("=" * 70)
print("FALSE NEGATIVE PROBABILITY ANALYSIS")
print("=" * 70)

print(
    f"\nFalse negatives at threshold 0.50: "
    f"{len(false_negatives)}"
)


if not false_negatives.empty:

    print(
        "\nProbability statistics:"
    )

    print(
        false_negatives[
            "phishing_probability"
        ].describe()
    )

    print(
        "\nLowest probability phishing emails:"
    )

    columns = [
        "true_label",
        "predicted_label",
        "phishing_probability",
        "risk_score",
        "graph_neighbors",
        "sender",
        "subject"
    ]

    available_columns = [
        column
        for column in columns
        if column in false_negatives.columns
    ]

    print(
        false_negatives[
            available_columns
        ]
        .sort_values(
            "phishing_probability"
        )
        .head(30)
        .to_string(
            index=False
        )
    )


# ============================================================
# PROBABILITY BANDS
# ============================================================

print("\n")
print("=" * 70)
print("PHISHING PROBABILITY BANDS")
print("=" * 70)

bands = [
    ("0.00 - 0.30", 0.00, 0.30),
    ("0.30 - 0.40", 0.30, 0.40),
    ("0.40 - 0.45", 0.40, 0.45),
    ("0.45 - 0.50", 0.45, 0.50),
    ("0.50 - 0.55", 0.50, 0.55),
    ("0.55 - 0.60", 0.55, 0.60),
    ("0.60 - 0.70", 0.60, 0.70),
    ("0.70 - 1.00", 0.70, 1.01)
]


for name, lower, upper in bands:

    subset = df[
        (
            df["phishing_probability"] >= lower
        )
        &
        (
            df["phishing_probability"] < upper
        )
    ]

    phishing_count = int(
        (
            subset["true_label"] == 1
        ).sum()
    )

    non_phishing_count = int(
        (
            subset["true_label"] == 0
        ).sum()
    )

    print(
        f"{name:15s} "
        f"Total={len(subset):5d} "
        f"Phishing={phishing_count:5d} "
        f"Non-Phishing={non_phishing_count:5d}"
    )


# ============================================================
# SAVE
# ============================================================

print("\n")
print("=" * 70)

print(
    f"Threshold analysis saved to:\n"
    f"{output_path}"
)

print("=" * 70)