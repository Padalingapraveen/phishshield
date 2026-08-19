import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "inference_evaluation"
)

PREDICTIONS_PATH = (
    RESULTS_DIR
    / "inference_predictions.csv"
)

THRESHOLD_RESULTS_PATH = (
    RESULTS_DIR
    / "threshold_analysis.csv"
)

BEST_THRESHOLD_PATH = (
    RESULTS_DIR
    / "best_threshold.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

THRESHOLDS = np.arange(
    0.30,
    0.601,
    0.01
)


# ============================================================
# LOAD PREDICTIONS
# ============================================================

print("=" * 70)
print("PHISHGUARD AI - THRESHOLD OPTIMIZATION")
print("=" * 70)

print("\nLoading saved predictions...")

df = pd.read_csv(
    PREDICTIONS_PATH
)

print(
    f"Predictions loaded: {len(df)}"
)

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

    raise ValueError(
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
# BASELINE
# ============================================================

print("\nCurrent baseline:")
print("-" * 70)

baseline_predictions = (
    probabilities >= 0.50
).astype(int)

baseline_cm = confusion_matrix(
    y_true,
    baseline_predictions,
    labels=[0, 1]
)

tn, fp, fn, tp = baseline_cm.ravel()

baseline_accuracy = accuracy_score(
    y_true,
    baseline_predictions
)

baseline_precision = precision_score(
    y_true,
    baseline_predictions,
    zero_division=0
)

baseline_recall = recall_score(
    y_true,
    baseline_predictions,
    zero_division=0
)

baseline_f1 = f1_score(
    y_true,
    baseline_predictions,
    zero_division=0
)

print(
    f"Threshold : 0.50"
)

print(
    f"Accuracy  : {baseline_accuracy:.6f}"
)

print(
    f"Precision : {baseline_precision:.6f}"
)

print(
    f"Recall    : {baseline_recall:.6f}"
)

print(
    f"F1        : {baseline_f1:.6f}"
)

print(
    f"TN={tn} FP={fp} FN={fn} TP={tp}"
)


# ============================================================
# THRESHOLD ANALYSIS
# ============================================================

results = []

print("\n")
print("=" * 70)
print("THRESHOLD ANALYSIS")
print("=" * 70)

for threshold in THRESHOLDS:

    predictions = (
        probabilities >= threshold
    ).astype(int)

    cm = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1]
    )

    tn, fp, fn, tp = cm.ravel()

    accuracy = accuracy_score(
        y_true,
        predictions
    )

    precision = precision_score(
        y_true,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        predictions,
        zero_division=0
    )

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )

    false_negative_rate = (
        fn / (fn + tp)
        if (fn + tp) > 0
        else 0
    )

    results.append(
        {
            "threshold": round(
                float(threshold),
                2
            ),

            "accuracy": accuracy,

            "precision": precision,

            "recall": recall,

            "f1": f1,

            "false_positive_rate":
                false_positive_rate,

            "false_negative_rate":
                false_negative_rate,

            "true_negatives": int(tn),

            "false_positives": int(fp),

            "false_negatives": int(fn),

            "true_positives": int(tp)
        }
    )


threshold_df = pd.DataFrame(
    results
)


# ============================================================
# PRINT TABLE
# ============================================================

print(
    "\n"
)

print(
    threshold_df[
        [
            "threshold",
            "accuracy",
            "precision",
            "recall",
            "f1",
            "false_positive_rate",
            "false_negative_rate",
            "false_positives",
            "false_negatives"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# BEST F1
# ============================================================

best_f1_row = (
    threshold_df
    .sort_values(
        [
            "f1",
            "recall",
            "precision"
        ],
        ascending=False
    )
    .iloc[0]
)


# ============================================================
# SECURITY-FOCUSED THRESHOLD
# ============================================================

# For phishing detection, missing phishing emails
# is more serious than generating some extra alerts.
#
# We therefore search for the threshold giving:
#
# 1. Recall >= 0.99 if possible
# 2. Highest precision among those thresholds
# 3. Highest F1 as tie breaker

high_recall_candidates = (
    threshold_df[
        threshold_df["recall"] >= 0.99
    ]
)

if not high_recall_candidates.empty:

    security_row = (
        high_recall_candidates
        .sort_values(
            [
                "precision",
                "f1",
                "recall"
            ],
            ascending=False
        )
        .iloc[0]
    )

else:

    security_row = (
        threshold_df
        .sort_values(
            [
                "recall",
                "f1",
                "precision"
            ],
            ascending=False
        )
        .iloc[0]
    )


# ============================================================
# BEST BALANCED THRESHOLD
# ============================================================

balanced_row = (
    threshold_df
    .sort_values(
        [
            "f1",
            "accuracy"
        ],
        ascending=False
    )
    .iloc[0]
)


# ============================================================
# PRINT BEST RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("BEST THRESHOLDS")
print("=" * 70)

print("\nBest F1 threshold:")

print(
    f"Threshold : {best_f1_row['threshold']:.2f}"
)

print(
    f"Accuracy  : {best_f1_row['accuracy']:.6f}"
)

print(
    f"Precision : {best_f1_row['precision']:.6f}"
)

print(
    f"Recall    : {best_f1_row['recall']:.6f}"
)

print(
    f"F1        : {best_f1_row['f1']:.6f}"
)

print(
    f"FP        : {int(best_f1_row['false_positives'])}"
)

print(
    f"FN        : {int(best_f1_row['false_negatives'])}"
)


print("\nSecurity-focused threshold:")

print(
    f"Threshold : {security_row['threshold']:.2f}"
)

print(
    f"Accuracy  : {security_row['accuracy']:.6f}"
)

print(
    f"Precision : {security_row['precision']:.6f}"
)

print(
    f"Recall    : {security_row['recall']:.6f}"
)

print(
    f"F1        : {security_row['f1']:.6f}"
)

print(
    f"FP        : {int(security_row['false_positives'])}"
)

print(
    f"FN        : {int(security_row['false_negatives'])}"
)


print("\nBalanced threshold:")

print(
    f"Threshold : {balanced_row['threshold']:.2f}"
)

print(
    f"Accuracy  : {balanced_row['accuracy']:.6f}"
)

print(
    f"Precision : {balanced_row['precision']:.6f}"
)

print(
    f"Recall    : {balanced_row['recall']:.6f}"
)

print(
    f"F1        : {balanced_row['f1']:.6f}"
)

print(
    f"FP        : {int(balanced_row['false_positives'])}"
)

print(
    f"FN        : {int(balanced_row['false_negatives'])}"
)


# ============================================================
# SAVE CSV
# ============================================================

threshold_df.to_csv(
    THRESHOLD_RESULTS_PATH,
    index=False
)


# ============================================================
# SAVE RECOMMENDED CONFIGURATION
# ============================================================

configuration = {

    "model":
        "DistilBERT + Graph Attention Network",

    "dataset":
        "CEAS-08",

    "evaluation_samples":
        int(len(df)),

    "baseline_threshold":
        0.50,

    "baseline_metrics": {
        "accuracy":
            float(baseline_accuracy),

        "precision":
            float(baseline_precision),

        "recall":
            float(baseline_recall),

        "f1":
            float(baseline_f1),

        "true_negatives":
            int(
                baseline_cm[0][0]
            ),

        "false_positives":
            int(
                baseline_cm[0][1]
            ),

        "false_negatives":
            int(
                baseline_cm[1][0]
            ),

        "true_positives":
            int(
                baseline_cm[1][1]
            )
    },

    "best_f1_threshold":
        float(
            best_f1_row["threshold"]
        ),

    "security_threshold":
        float(
            security_row["threshold"]
        ),

    "recommended_initial_threshold":
        float(
            security_row["threshold"]
        )
}


with open(
    BEST_THRESHOLD_PATH,
    "w"
) as f:

    json.dump(
        configuration,
        f,
        indent=4
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n")
print("=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    "\nThreshold analysis:"
)

print(
    THRESHOLD_RESULTS_PATH
)

print(
    "\nRecommended threshold configuration:"
)

print(
    BEST_THRESHOLD_PATH
)

print("\nThreshold optimization complete.")