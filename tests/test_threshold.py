def test_classification_threshold():

    threshold = 0.47

    # Below threshold -> NON-PHISHING
    assert int(0.4699 >= threshold) == 0

    # Exactly threshold -> PHISHING
    assert int(0.4700 >= threshold) == 1

    # Above threshold -> PHISHING
    assert int(0.5000 >= threshold) == 1

    # High probability -> PHISHING
    assert int(0.6000 >= threshold) == 1


def test_risk_levels():

    assert get_risk_level(0.40) == "LOW"
    assert get_risk_level(0.47) == "MEDIUM"
    assert get_risk_level(0.59) == "MEDIUM"
    assert get_risk_level(0.60) == "HIGH"
    assert get_risk_level(0.79) == "HIGH"
    assert get_risk_level(0.80) == "CRITICAL"


def get_risk_level(probability):

    if probability < 0.47:
        return "LOW"

    elif probability < 0.60:
        return "MEDIUM"

    elif probability < 0.80:
        return "HIGH"

    else:
        return "CRITICAL"