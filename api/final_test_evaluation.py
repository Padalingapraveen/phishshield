import json
import time
from pathlib import Path

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

from api.predictor import PhishGuardPredictor


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEPLOYMENT_DIR = (
    PROJECT_ROOT
    / "models"
    / "distilbert_gat"
    / "deployment"
)

# IMPORTANT:
# Use the untouched TEST dataset here.
TEST_DATASET = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "test.csv"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "test_evaluation"
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIGURATION
# ============================================================

THRESHOLD = 0.47


# ============================================================
# LOAD TEST DATA
# ============================================================

print("=" * 70)
print("PHISHGUARD AI - FINAL TEST SET EVALUATION")
print("=" * 70)

print("\nLoading untouched test dataset...")

df = pd.read_csv(TEST_DATASET)

print(
    f"Test dataset shape: {df.shape}"
)

print("\nLabel distribution:")
print(
    df["label"].value_counts()
)

print(
    f"\nOperating threshold: {THRESHOLD}"
)


# ============================================================
# VALIDATE DATA
# ============================================================

required_columns = [
    "sender",
    "receiver",
    "subject",
    "body",
    "label"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        f"Missing required columns: "
        f"{missing_columns}"
    )


# ============================================================
# LOAD PRODUCTION PREDICTOR
# ============================================================

print("\nLoading production predictor...")

predictor = PhishGuardPredictor()

print(
    "\nProduction predictor loaded successfully."
)


# ============================================================
# RUN TEST INFERENCE
# ============================================================

results = []

errors = 0

start_time = time.perf_counter()

print("\nRunning inference...")
print("-" * 70)

total = len(df)

for index, row in df.iterrows():

    email = {
        "sender": str(row.get("sender", "")),
        "receiver": str(row.get("receiver", "")),
        "subject": str(row.get("subject", "")),
        "body": str(row.get("body", ""))
    }

    true_label = int(row["label"])

    try:

        prediction = predictor.predict(
            email["sender"],
            email["receiver"],
            email["subject"],
            email["body"]
        )

        phishing_probability = float(
            prediction["phishing_probability"]
        )

        # ====================================================
        # IMPORTANT:
        # USE OPTIMIZED THRESHOLD 0.47
        # ====================================================

        predicted_label = int(
            phishing_probability >= THRESHOLD
        )

        results.append(
            {
                "index": index,

                "true_label":
                    true_label,

                "predicted_label":
                    predicted_label,

                "phishing_probability":
                    phishing_probability,

                "non_phishing_probability":
                    float(
                        prediction[
                            "non_phishing_probability"
                        ]
                    ),

                "risk_score":
                    float(
                        prediction[
                            "risk_score"
                        ]
                    ),

                "graph_neighbors":
                    int(
                        prediction[
                            "graph_neighbors"
                        ]
                    ),

                "sender":
                    email["sender"],

                "receiver":
                    email["receiver"],

                "subject":
                    email["subject"],

                "correct":
                    true_label == predicted_label
            }
        )

        # Print every 100 emails instead of
        # flooding the terminal.

        if (
            (index + 1) % 100 == 0
            or index == 0
        ):

            print(
                f"[{index + 1:05d}/{total}] "
                f"True={true_label} "
                f"Pred={predicted_label} "
                f"PhishingProb="
                f"{phishing_probability:.4f}"
            )

    except Exception as e:

        errors += 1

        print(
            f"[{index + 1:05d}] ERROR: {e}"
        )


end_time = time.perf_counter()

total_inference_seconds = (
    end_time - start_time
)


# ============================================================
# CHECK RESULTS
# ============================================================

results_df = pd.DataFrame(results)

if results_df.empty:

    raise RuntimeError(
        "No predictions were generated."
    )


print("\n")
print("=" * 70)
print("INFERENCE COMPLETED")
print("=" * 70)

print(
    f"Predictions : {len(results_df)}"
)

print(
    f"Errors      : {errors}"
)

print(
    f"Time        : "
    f"{total_inference_seconds:.2f} seconds"
)


# ============================================================
# METRICS
# ============================================================

y_true = results_df[
    "true_label"
].values

y_pred = results_df[
    "predicted_label"
].values

y_probability = results_df[
    "phishing_probability"
].values


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

try:

    roc_auc = roc_auc_score(
        y_true,
        y_probability
    )

except ValueError:

    roc_auc = None


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1]
)

tn, fp, fn, tp = cm.ravel()


# ============================================================
# ERROR RATES
# ============================================================

false_positive_rate = (
    fp / (fp + tn)
    if (fp + tn) > 0
    else 0.0
)

false_negative_rate = (
    fn / (fn + tp)
    if (fn + tp) > 0
    else 0.0
)


# ============================================================
# SPEED
# ============================================================

total_predictions = len(results_df)

emails_per_second = (
    total_predictions
    / total_inference_seconds
    if total_inference_seconds > 0
    else 0.0
)

milliseconds_per_email = (
    total_inference_seconds
    * 1000
    / total_predictions
    if total_predictions > 0
    else 0.0
)


# ============================================================
# PRINT FINAL RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("FINAL TEST SET RESULTS")
print("=" * 70)

print(
    f"Samples             : "
    f"{total_predictions}"
)

print(
    f"Errors              : "
    f"{errors}"
)

print(
    f"Threshold           : "
    f"{THRESHOLD:.2f}"
)

print(
    f"Accuracy            : "
    f"{accuracy:.6f}"
)

print(
    f"Precision           : "
    f"{precision:.6f}"
)

print(
    f"Recall              : "
    f"{recall:.6f}"
)

print(
    f"F1 Score            : "
    f"{f1:.6f}"
)

if roc_auc is not None:

    print(
        f"ROC-AUC             : "
        f"{roc_auc:.6f}"
    )

print(
    f"False Positive Rate : "
    f"{false_positive_rate:.6f}"
)

print(
    f"False Negative Rate : "
    f"{false_negative_rate:.6f}"
)

print("\nConfusion Matrix:")

print(cm)

print(
    f"\nTN: {tn}"
)

print(
    f"FP: {fp}"
)

print(
    f"FN: {fn}"
)

print(
    f"TP: {tp}"
)

print("\nInference Performance:")

print(
    f"Total time          : "
    f"{total_inference_seconds:.3f} sec"
)

print(
    f"Emails/second       : "
    f"{emails_per_second:.4f}"
)

print(
    f"Milliseconds/email  : "
    f"{milliseconds_per_email:.4f} ms"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "NON-PHISHING",
            "PHISHING"
        ],
        zero_division=0
    )
)


# ============================================================
# FALSE NEGATIVES
# ============================================================

false_negatives = results_df[
    (
        results_df["true_label"] == 1
    )
    &
    (
        results_df["predicted_label"] == 0
    )
]

print("\n")
print("=" * 70)
print("FALSE NEGATIVES")
print("=" * 70)

print(
    f"Total false negatives: "
    f"{len(false_negatives)}"
)

if not false_negatives.empty:

    print(
        false_negatives[
            [
                "true_label",
                "predicted_label",
                "phishing_probability",
                "risk_score",
                "graph_neighbors",
                "sender",
                "subject"
            ]
        ].to_string(
            index=False
        )
    )


# ============================================================
# FALSE POSITIVES
# ============================================================

false_positives = results_df[
    (
        results_df["true_label"] == 0
    )
    &
    (
        results_df["predicted_label"] == 1
    )
]

print("\n")
print("=" * 70)
print("FALSE POSITIVES")
print("=" * 70)

print(
    f"Total false positives: "
    f"{len(false_positives)}"
)

if not false_positives.empty:

    print(
        false_positives[
            [
                "true_label",
                "predicted_label",
                "phishing_probability",
                "risk_score",
                "graph_neighbors",
                "sender",
                "subject"
            ]
        ].to_string(
            index=False
        )
    )


# ============================================================
# SAVE PREDICTIONS
# ============================================================

predictions_path = (
    RESULTS_DIR
    / "test_predictions_threshold_047.csv"
)

results_df.to_csv(
    predictions_path,
    index=False
)


# ============================================================
# SAVE METRICS
# ============================================================

metrics = {

    "model":
        "DistilBERT + Graph Attention Network",

    "dataset":
        "CEAS-08",

    "evaluation_split":
        "test",

    "samples":
        int(total_predictions),

    "errors":
        int(errors),

    "threshold":
        float(THRESHOLD),

    "accuracy":
        float(accuracy),

    "precision":
        float(precision),

    "recall":
        float(recall),

    "f1":
        float(f1),

    "roc_auc":
        (
            float(roc_auc)
            if roc_auc is not None
            else None
        ),

    "confusion_matrix":
        cm.tolist(),

    "true_negatives":
        int(tn),

    "false_positives":
        int(fp),

    "false_negatives":
        int(fn),

    "true_positives":
        int(tp),

    "false_positive_rate":
        float(false_positive_rate),

    "false_negative_rate":
        float(false_negative_rate),

    "total_inference_seconds":
        float(total_inference_seconds),

    "emails_per_second":
        float(emails_per_second),

    "milliseconds_per_email":
        float(milliseconds_per_email)
}


metrics_path = (
    RESULTS_DIR
    / "test_metrics_threshold_047.json"
)

with open(
    metrics_path,
    "w"
) as f:

    json.dump(
        metrics,
        f,
        indent=4
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n")
print("=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    f"Predictions:\n"
    f"{predictions_path}"
)

print(
    f"\nMetrics:\n"
    f"{metrics_path}"
)

print("\nFinal test evaluation complete.")