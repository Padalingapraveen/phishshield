from pydantic import BaseModel


class EmailRequest(BaseModel):
    sender: str = ""
    receiver: str = ""
    subject: str = ""
    body: str = ""


class PredictionResponse(BaseModel):
    label: str
    phishing_probability: float
    non_phishing_probability: float
    risk_score: float