import json
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "inference_evaluation"
)

PREDICTIONS_FILE = (
    RESULTS_DIR
    / "inference_predictions.csv"
)

OUTPUT_DIR = (
    RESULTS_DIR
    / "error_analysis"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD RESULTS
# ============================================================

print("=" * 70)
print("PHISHGUARD AI - INFERENCE ERROR ANALYSIS")
print("=" * 70)

print("\nLoading predictions...")

df = pd.read_csv(
    PREDICTIONS_FILE
)

print(
    f"Total predictions: {len(df)}"
)


# ============================================================
# FALSE NEGATIVES
# ============================================================

false_negatives = df[
    (df["true_label"] == 1)
    &
    (df["predicted_label"] == 0)
].copy()


# ============================================================
# FALSE POSITIVES
# ============================================================

false_positives = df[
    (df["true_label"] == 0)
    &
    (df["predicted_label"] == 1)
].copy()


print("\n")
print("=" * 70)
print("ERROR SUMMARY")
print("=" * 70)

print(
    f"False Negatives : {len(false_negatives)}"
)

print(
    f"False Positives : {len(false_positives)}"
)


# ============================================================
# FALSE NEGATIVE PROBABILITY ANALYSIS
# ============================================================

print("\n")
print("=" * 70)
print("FALSE NEGATIVE PROBABILITY ANALYSIS")
print("=" * 70)

if not false_negatives.empty:

    print(
        false_negatives[
            [
                "index",
                "phishing_probability",
                "risk_score",
                "graph_neighbors",
                "sender",
                "receiver",
                "subject"
            ]
        ].to_string(
            index=False
        )
    )

    print("\nFalse-negative probability statistics:")

    print(
        false_negatives[
            "phishing_probability"
        ].describe()
    )


# ============================================================
# FALSE POSITIVE PROBABILITY ANALYSIS
# ============================================================

print("\n")
print("=" * 70)
print("FALSE POSITIVE PROBABILITY ANALYSIS")
print("=" * 70)

if not false_positives.empty:

    print(
        false_positives[
            [
                "index",
                "phishing_probability",
                "risk_score",
                "graph_neighbors",
                "sender",
                "receiver",
                "subject"
            ]
        ].to_string(
            index=False
        )
    )

    print("\nFalse-positive probability statistics:")

    print(
        false_positives[
            "phishing_probability"
        ].describe()
    )


# ============================================================
# PROBABILITY RANGES
# ============================================================

print("\n")
print("=" * 70)
print("ERROR PROBABILITY RANGES")
print("=" * 70)


bins = [
    0.0,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.80,
    0.90,
    1.01
]

labels = [
    "<40%",
    "40-45%",
    "45-50%",
    "50-55%",
    "55-60%",
    "60-65%",
    "65-70%",
    "70-80%",
    "80-90%",
    "90%+"
]


if not false_negatives.empty:

    fn_ranges = pd.cut(
        false_negatives[
            "phishing_probability"
        ],
        bins=bins,
        labels=labels,
        right=False
    )

    print("\nFalse negatives by probability:")

    print(
        fn_ranges.value_counts(
            sort=False
        )
    )


if not false_positives.empty:

    fp_ranges = pd.cut(
        false_positives[
            "phishing_probability"
        ],
        bins=bins,
        labels=labels,
        right=False
    )

    print("\nFalse positives by probability:")

    print(
        fp_ranges.value_counts(
            sort=False
        )
    )


# ============================================================
# LOW-CONFIDENCE PREDICTIONS
# ============================================================

print("\n")
print("=" * 70)
print("LOW-CONFIDENCE PREDICTIONS")
print("=" * 70)

df["distance_from_boundary"] = (
    df["phishing_probability"] - 0.50
).abs()

low_confidence = df.sort_values(
    "distance_from_boundary"
).head(50)


print(
    low_confidence[
        [
            "index",
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
# ERROR BY GRAPH NEIGHBOR COUNT
# ============================================================

print("\n")
print("=" * 70)
print("GRAPH NEIGHBOR ANALYSIS")
print("=" * 70)

if not false_negatives.empty:

    print(
        "\nFalse-negative graph neighbors:"
    )

    print(
        false_negatives[
            "graph_neighbors"
        ].describe()
    )


if not false_positives.empty:

    print(
        "\nFalse-positive graph neighbors:"
    )

    print(
        false_positives[
            "graph_neighbors"
        ].describe()
    )


# ============================================================
# SAVE FALSE NEGATIVES
# ============================================================

fn_path = (
    OUTPUT_DIR
    / "false_negatives.csv"
)

false_negatives.to_csv(
    fn_path,
    index=False
)


# ============================================================
# SAVE FALSE POSITIVES
# ============================================================

fp_path = (
    OUTPUT_DIR
    / "false_positives.csv"
)

false_positives.to_csv(
    fp_path,
    index=False
)


# ============================================================
# SAVE LOW CONFIDENCE
# ============================================================

low_confidence_path = (
    OUTPUT_DIR
    / "low_confidence_predictions.csv"
)

low_confidence.to_csv(
    low_confidence_path,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

summary = {
    "total_predictions": int(len(df)),
    "false_negatives": int(len(false_negatives)),
    "false_positives": int(len(false_positives)),
    "false_negative_rate": (
        float(
            len(false_negatives)
            /
            len(df[df["true_label"] == 1])
        )
        if len(df[df["true_label"] == 1]) > 0
        else 0
    ),
    "false_positive_rate": (
        float(
            len(false_positives)
            /
            len(df[df["true_label"] == 0])
        )
        if len(df[df["true_label"] == 0]) > 0
        else 0
    )
}


summary_path = (
    OUTPUT_DIR
    / "error_analysis_summary.json"
)

with open(
    summary_path,
    "w"
) as f:

    json.dump(
        summary,
        f,
        indent=4
    )


# ============================================================
# FINAL
# ============================================================

print("\n")
print("=" * 70)
print("ERROR ANALYSIS FILES")
print("=" * 70)

print(
    "\nFalse negatives:"
)

print(
    fn_path
)

print(
    "\nFalse positives:"
)

print(
    fp_path
)

print(
    "\nLow-confidence predictions:"
)

print(
    low_confidence_path
)

print(
    "\nSummary:"
)

print(
    summary_path
)

print("\nAnalysis complete.")