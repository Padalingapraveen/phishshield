from api.model import DistilBERTGAT


def test_model_initializes():
    model = DistilBERTGAT()
    assert model is not None

