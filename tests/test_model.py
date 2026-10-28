import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from api.model import DistilBERTGAT


def test_model_initializes():
    model = DistilBERTGAT()
    assert model is not None

