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

REFERENCE_DATASET = (
    DEPLOYMENT_DIR
    / "reference_emails.csv"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "inference_evaluation"
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIGURATION
# ============================================================

# None = evaluate entire dataset
SAMPLES_PER_CLASS = 1000

# Print progress every N emails
PROGRESS_INTERVAL = 100

# Save intermediate results every N emails
CHECKPOINT_INTERVAL = 1000


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PHISHGUARD AI - PRODUCTION INFERENCE EVALUATION")
print("=" * 70)

print("\nLoading reference dataset...")

df = pd.read_csv(
    REFERENCE_DATASET
)

print(f"Dataset shape: {df.shape}")

print("\nLabel distribution:")
print(df["label"].value_counts())


# ============================================================
# SELECT DATA
# ============================================================

if SAMPLES_PER_CLASS is None:

    evaluation_df = df.copy()

else:

    phishing_df = df[
        df["label"] == 1
    ].sample(
        n=min(
            SAMPLES_PER_CLASS,
            len(df[df["label"] == 1])
        ),
        random_state=42
    )

    non_phishing_df = df[
        df["label"] == 0
    ].sample(
        n=min(
            SAMPLES_PER_CLASS,
            len(df[df["label"] == 0])
        ),
        random_state=42
    )

    evaluation_df = pd.concat(
        [
            phishing_df,
            non_phishing_df
        ]
    ).sample(
        frac=1,
        random_state=42
    )


evaluation_df = evaluation_df.reset_index(drop=True)

print(
    f"\nEvaluation samples: {len(evaluation_df)}"
)


# ============================================================
# LOAD PREDICTOR
# ============================================================

print("\nLoading production predictor...")

start_load = time.time()

predictor = PhishGuardPredictor()

load_time = time.time() - start_load

print(
    f"\nPredictor loaded in {load_time:.2f} seconds."
)


# ============================================================
# INFERENCE
# ============================================================

results = []

errors = []

start_time = time.time()

print("\nRunning inference...")
print("-" * 70)


for index, row in evaluation_df.iterrows():

    email = {
        "sender": str(row.get("sender", "")),
        "receiver": str(row.get("receiver", "")),
        "subject": str(row.get("subject", "")),
        "body": str(row.get("body", ""))
    }

    true_label = int(row["label"])

    try:

        # IMPORTANT:
        # predictor.predict expects 4 separate arguments
        prediction = predictor.predict(
            email["sender"],
            email["receiver"],
            email["subject"],
            email["body"]
        )

        predicted_label = int(
            prediction["predicted_class"]
        )

        phishing_probability = float(
            prediction["phishing_probability"]
        )

        risk_score = float(
            prediction["risk_score"]
        )

        graph_neighbors = int(
            prediction["graph_neighbors"]
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

                "risk_score":
                    risk_score,

                "graph_neighbors":
                    graph_neighbors,

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

    except Exception as e:

        errors.append(
            {
                "index": index,
                "error": str(e)
            }
        )

        print(
            f"[ERROR {index + 1}] {e}"
        )

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    processed = index + 1

    if (
        processed % PROGRESS_INTERVAL == 0
        or processed == len(evaluation_df)
    ):

        elapsed = time.time() - start_time

        speed = (
            processed / elapsed
            if elapsed > 0
            else 0
        )

        remaining = (
            len(evaluation_df) - processed
        )

        eta = (
            remaining / speed
            if speed > 0
            else 0
        )

        print(
            f"[{processed:05d}/{len(evaluation_df)}] "
            f"Speed={speed:.2f} emails/sec "
            f"ETA={eta / 60:.2f} min"
        )

    # --------------------------------------------------------
    # CHECKPOINT
    # --------------------------------------------------------

    if (
        processed % CHECKPOINT_INTERVAL == 0
        and results
    ):

        checkpoint_path = (
            RESULTS_DIR
            / "inference_checkpoint.csv"
        )

        pd.DataFrame(
            results
        ).to_csv(
            checkpoint_path,
            index=False
        )


# ============================================================
# CHECK RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)

if results_df.empty:

    raise RuntimeError(
        "No predictions were generated."
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
# TIMING
# ============================================================

total_time = time.time() - start_time

emails_per_second = (
    len(results_df) / total_time
    if total_time > 0
    else 0
)


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("INFERENCE EVALUATION RESULTS")
print("=" * 70)

print(
    f"Samples             : {len(results_df)}"
)

print(
    f"Errors              : {len(errors)}"
)

print(
    f"Accuracy            : {accuracy:.6f}"
)

print(
    f"Precision           : {precision:.6f}"
)

print(
    f"Recall              : {recall:.6f}"
)

print(
    f"F1 Score            : {f1:.6f}"
)

if roc_auc is not None:

    print(
        f"ROC-AUC             : {roc_auc:.6f}"
    )

print(
    f"\nTotal inference time: {total_time:.2f} sec"
)

print(
    f"Speed               : {emails_per_second:.2f} emails/sec"
)

print(
    f"Time per email      : "
    f"{(total_time / len(results_df)) * 1000:.2f} ms"
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")
print(cm)

print("\nTN:", tn)
print("FP:", fp)
print("FN:", fn)
print("TP:", tp)


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
    (results_df["true_label"] == 1)
    &
    (results_df["predicted_label"] == 0)
]

print("\n")
print("=" * 70)
print("FALSE NEGATIVES")
print("=" * 70)

if false_negatives.empty:

    print(
        "No false negatives found."
    )

else:

    print(
        false_negatives[
            [
                "index",
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
    (results_df["true_label"] == 0)
    &
    (results_df["predicted_label"] == 1)
]

print("\n")
print("=" * 70)
print("FALSE POSITIVES")
print("=" * 70)

if false_positives.empty:

    print(
        "No false positives found."
    )

else:

    print(
        false_positives[
            [
                "index",
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
    / "inference_predictions.csv"
)

results_df.to_csv(
    predictions_path,
    index=False
)


# ============================================================
# SAVE ERRORS
# ============================================================

errors_path = (
    RESULTS_DIR
    / "inference_errors.json"
)

with open(
    errors_path,
    "w"
) as f:

    json.dump(
        errors,
        f,
        indent=4
    )


# ============================================================
# SAVE METRICS
# ============================================================

metrics = {
    "samples": int(len(results_df)),

    "errors": int(len(errors)),

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

    "total_inference_seconds":
        float(total_time),

    "emails_per_second":
        float(emails_per_second),

    "milliseconds_per_email":
        float(
            (total_time / len(results_df))
            * 1000
        )
}


metrics_path = (
    RESULTS_DIR
    / "inference_metrics.json"
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
# FINAL
# ============================================================

print("\n")
print("=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    "\nPredictions:"
)

print(
    predictions_path
)

print(
    "\nMetrics:"
)

print(
    metrics_path
)

print(
    "\nErrors:"
)

print(
    errors_path
)

print("\nEvaluation complete.")