from pydantic import BaseModel


class EmailRequest(BaseModel):
    sender: str = ""
    receiver: str = ""
    subject: str = ""
    body: str
    source: str = "web"

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None


class PredictionResponse(BaseModel):
    label: str
    phishing_probability: float
    non_phishing_probability: float
    risk_score: float