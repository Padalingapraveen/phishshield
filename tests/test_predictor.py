import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"

if VENV_PYTHON.exists() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

sys.path.insert(0, str(ROOT_DIR))

from api.predictor import PhishGuardPredictor


def print_result(name, result):
    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print("Label:", result["label"])
    print("Predicted class:", result["predicted_class"])

    print(
        "Phishing probability:",
        f'{result["phishing_probability"]:.6f}'
    )

    print(
        "Non-phishing probability:",
        f'{result["non_phishing_probability"]:.6f}'
    )

    print(
        "Risk score:",
        f'{result["risk_score"]:.2f}%'
    )

    print("Risk level:", result["risk_level"])
    print("Graph neighbors:", result["graph_neighbors"])
    print("Graph edge types:", result["graph_edge_types"])

    print("Sender:", result["sender_entity"])
    print("Receiver:", result["receiver_entity"])
    print("Domains:", result["domain_entities"])


predictor = PhishGuardPredictor()


# ============================================================
# TEST 1 - NORMAL EMAIL
# ============================================================

result = predictor.predict(
    sender="teacher@college.edu",
    receiver="student@gmail.com",
    subject="Tomorrow's class schedule",
    body="The class will begin at 10 AM tomorrow. Please attend on time."
)

print_result(
    "TEST 1 - NORMAL EMAIL",
    result
)


# ============================================================
# TEST 2 - SUSPICIOUS EMAIL
# ============================================================

result = predictor.predict(
    sender="security@paypa1-alert.com",
    receiver="user@gmail.com",
    subject="Urgent: Your account will be suspended",
    body=(
        "Your account will be suspended immediately. "
        "Verify your account and password now."
    )
)

print_result(
    "TEST 2 - SUSPICIOUS EMAIL",
    result
)


# ============================================================
# TEST 3 - PASSWORD REQUEST
# ============================================================

result = predictor.predict(
    sender="admin@secure-check.com",
    receiver="user@gmail.com",
    subject="Verify your account",
    body=(
        "Your account requires verification. "
        "Please provide your password immediately."
    )
)

print_result(
    "TEST 3 - PASSWORD REQUEST",
    result
)
