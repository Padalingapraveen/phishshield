import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from api.performance_service import (
    get_performance_data,
    generate_all_charts,
    CHARTS_DIR
)
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from collections import Counter
from pydantic import BaseModel, Field

from api.models import DetectionEvent, User
from api.schemas import EmailRequest, PredictionResponse, UserCreate, UserResponse, Token
from api.database import get_db, init_database
from api.predictor import PhishGuardPredictor
from api.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from fastapi.middleware.cors import CORSMiddleware
from api.config import (
    CORS_ORIGINS,
    RATE_LIMIT_LOGIN,
    RATE_LIMIT_REGISTER,
    RATE_LIMIT_PREDICT
)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

def get_risk_level(score):
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 47:
        return "MEDIUM"
    return "LOW"

ml_models = {}

EXTENSION_CONFIG = {
    "enabled": True,
    "last_connected": None,
    "total_scans": 0
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    logger.info("Starting PhishGuard API. Loading Predictor...")
    try:
        ml_models["predictor"] = PhishGuardPredictor()
        logger.info("Predictor loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load Predictor: {e}")
    yield
    ml_models.clear()
    logger.info("PhishGuard API shutting down.")

app = FastAPI(
    title="PhishGuard AI",
    description=(
        "DistilBERT + Graph Attention "
        "Network Phishing Detection API"
    ),
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Limiter
# Note: In-memory storage is used here (suitable for single-process). 
# If scaling horizontally, a Redis backend is required.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --------------------------------------------------
# Initialize database
# --------------------------------------------------

init_database()


# --------------------------------------------------
# Note: Predictor is now loaded in lifespan context
# --------------------------------------------------

# --------------------------------------------------
# Auth routes
# --------------------------------------------------

@app.post("/auth/register", response_model=UserResponse)
@limiter.limit(RATE_LIMIT_REGISTER)
def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role="user")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login")
@limiter.limit(RATE_LIMIT_LOGIN)
def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not authenticate_user(user, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    
    from api.config import COOKIE_SECURE
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    
    return {"access_token": access_token, "token_type": "bearer", "message": "Logged in successfully"}

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"message": "Logged out successfully"}

@app.get("/auth/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# --------------------------------------------------
# Request schema
# --------------------------------------------------

MAX_SENDER_LENGTH = 320
MAX_RECEIVER_LENGTH = 320
MAX_SUBJECT_LENGTH = 998
MAX_BODY_LENGTH = 50000

class EmailRequest(BaseModel):
    sender: str = Field(..., max_length=MAX_SENDER_LENGTH)
    receiver: str = Field(..., max_length=MAX_RECEIVER_LENGTH)
    subject: str = Field(..., max_length=MAX_SUBJECT_LENGTH)
    body: str = Field(..., max_length=MAX_BODY_LENGTH)
    source: str = "web"


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "PhishGuard AI",
        "status": "running"
    }


# --------------------------------------------------
# Health
# --------------------------------------------------
from sqlalchemy import text

@app.get("/health")
def health(db: Session = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "api": "online",
        "predictor": "online",
        "database": "online",
        "extension": "online" if EXTENSION_CONFIG.get("enabled", False) else "offline"
    }
    
    if "predictor" not in ml_models or ml_models["predictor"] is None:
        health_status["status"] = "degraded"
        health_status["predictor"] = "offline"
        
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        health_status["status"] = "degraded"
        health_status["database"] = "offline"
        
    return health_status


# --------------------------------------------------
# Prediction
# --------------------------------------------------

@app.post("/predict")
@limiter.limit(RATE_LIMIT_PREDICT)
def predict_email(
    request: Request,
    email_request: EmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # ========================================================
    # 1. PREDICTOR AVAILABILITY CHECK
    # ========================================================
    predictor = ml_models.get("predictor")
    if not predictor:
        raise HTTPException(status_code=503, detail="Predictor unavailable")

    # ========================================================
    # 2. MODEL PREDICTION
    # ========================================================
    try:
        result = predictor.predict(
            sender=email_request.sender,
            receiver=email_request.receiver,
            subject=email_request.subject,
            body=email_request.body
        )
    except Exception as e:
        logger.error(f"Predictor raised an error during inference: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed due to an internal error.")

    # ========================================================
    # 3. SAVE DETECTION EVENT (OPTIONAL, ASYNC TO PREDICTION)
    # ========================================================
    try:
        event = DetectionEvent(
            sender=email_request.sender,
            receiver=email_request.receiver,
            subject=email_request.subject,
            label=result["label"],
            predicted_class=result["predicted_class"],
            phishing_probability=result["phishing_probability"],
            non_phishing_probability=result["non_phishing_probability"],
            risk_score=result["risk_score"],
            graph_neighbors=result["graph_neighbors"],
            graph_edge_types=json.dumps(result["graph_edge_types"]),
            sender_entity=result["sender_entity"],
            receiver_entity=result["receiver_entity"],
            domain_entities=json.dumps(result["domain_entities"]),
            user_id=current_user.id
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        
        # We append DB metadata, though core predictor logic generated the ML metrics
        result["event_id"] = event.id
        result["timestamp"] = event.timestamp.isoformat()
    except Exception as e:
        logger.error(f"Failed to log detection event to database: {e}")
        # We still return the ML prediction even if DB logging fails

    # ========================================================
    # 4. RETURN FINAL RESPONSE
    # ========================================================
    return result


    # ----------------------------------------------
    # Add event ID to API response
    # ----------------------------------------------

  

@app.get("/events")
def get_events(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    if offset < 0:
        offset = 0

    query = db.query(DetectionEvent)
    if current_user.role != "admin":
        query = query.filter(DetectionEvent.user_id == current_user.id)

    events = (
        query.order_by(
            DetectionEvent.timestamp.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [

        {
            "id": event.id,

            "timestamp":
                event.timestamp.isoformat(),

            "sender":
                event.sender,

            "receiver":
                event.receiver,

            "subject":
                event.subject,

            "label":
                event.label,

            "predicted_class":
                event.predicted_class,

            "phishing_probability":
                event.phishing_probability,

            "non_phishing_probability":
                event.non_phishing_probability,

            "risk_score":
                event.risk_score,

            "risk_level":
                get_risk_level(
                    event.risk_score
                ),

            "graph_neighbors":
                event.graph_neighbors
        }

        for event in events
    ]



   

@app.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):

    total = (
        db.query(DetectionEvent)
        .count()
    )


    phishing = (

        db.query(DetectionEvent)

        .filter(
            DetectionEvent.predicted_class == 1
        )

        .count()

    )


    non_phishing = (

        db.query(DetectionEvent)

        .filter(
            DetectionEvent.predicted_class == 0
        )

        .count()

    )


    average_risk = 0.0


    if total > 0:

        events = (
            db.query(
                DetectionEvent.risk_score
            )
            .all()
        )

        average_risk = (

            sum(
                event[0]
                for event in events
            )
            / total

        )


    return {

        "total_events":
            total,

        "phishing_events":
            phishing,

        "non_phishing_events":
            non_phishing,

        "average_risk_score":
            average_risk

    }

# ============================================================
# NEW ADMIN ENDPOINTS (TASK 5)
# ============================================================

@app.get("/admin/users")
def admin_get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "role": u.role, "is_active": u.is_active} for u in users]

@app.get("/admin/scans")
def admin_get_scans(limit: int = 100, offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Equivalent to old /events behavior for admins
    return get_events(limit=limit, offset=offset, db=db, current_user=current_user)

@app.get("/admin/stats")
def admin_get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    total = db.query(DetectionEvent).count()
    phishing = db.query(DetectionEvent).filter(DetectionEvent.predicted_class == 1).count()
    non_phishing = db.query(DetectionEvent).filter(DetectionEvent.predicted_class == 0).count()
    high_risk = db.query(DetectionEvent).filter(DetectionEvent.risk_score >= 60, DetectionEvent.risk_score < 80).count()
    critical_risk = db.query(DetectionEvent).filter(DetectionEvent.risk_score >= 80).count()
    recent = db.query(DetectionEvent).filter(DetectionEvent.timestamp >= datetime.utcnow() - timedelta(hours=24)).count()

    return {
        "total_scans": total,
        "phishing_count": phishing,
        "non_phishing_count": non_phishing,
        "high_risk_count": high_risk,
        "critical_risk_count": critical_risk,
        "recent_scan_count": recent
    }

# ============================================================
# SOC DASHBOARD ENDPOINTS
# ============================================================
@app.get("/dashboard/overview")
def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Scope to user's own events unless admin
    base_query = db.query(DetectionEvent)
    if current_user.role != "admin":
        base_query = base_query.filter(DetectionEvent.user_id == current_user.id)

    total_events = base_query.count()

    phishing_events = (
        base_query
        .filter(DetectionEvent.predicted_class == 1)
        .count()
    )

    non_phishing_events = (
        base_query
        .filter(DetectionEvent.predicted_class == 0)
        .count()
    )

    critical_events = base_query.filter(DetectionEvent.risk_score >= 80).count()
    high_events = base_query.filter(DetectionEvent.risk_score >= 60, DetectionEvent.risk_score < 80).count()
    medium_events = base_query.filter(DetectionEvent.risk_score >= 47, DetectionEvent.risk_score < 60).count()
    low_events = base_query.filter(DetectionEvent.risk_score < 47).count()

    risk_values = base_query.with_entities(DetectionEvent.risk_score).all()
    average_risk_score = (
        sum(row[0] for row in risk_values) / len(risk_values)
        if risk_values else 0.0
    )

    return {
        "total_events": total_events,
        "phishing_events": phishing_events,
        "non_phishing_events": non_phishing_events,
        "phishing_percentage": round(phishing_events / total_events * 100, 2) if total_events > 0 else 0.0,
        "non_phishing_percentage": round(non_phishing_events / total_events * 100, 2) if total_events > 0 else 0.0,
        "average_risk_score": round(average_risk_score, 2),
        "risk_distribution": {
            "critical": critical_events,
            "high": high_events,
            "medium": medium_events,
            "low": low_events
        }
    }
# ============================================================
# PHISHING VS NON-PHISHING DISTRIBUTION
# ============================================================

@app.get("/dashboard/distribution")
def dashboard_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    base_query = db.query(DetectionEvent)
    if current_user.role != "admin":
        base_query = base_query.filter(DetectionEvent.user_id == current_user.id)

    phishing = base_query.filter(DetectionEvent.predicted_class == 1).count()
    non_phishing = base_query.filter(DetectionEvent.predicted_class == 0).count()

    return {
        "labels": ["Phishing", "Non-Phishing"],
        "values": [phishing, non_phishing]
    }


# ============================================================
# RISK DISTRIBUTION
# ============================================================

@app.get("/dashboard/risk-distribution")
def dashboard_risk_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    base_query = db.query(DetectionEvent)
    if current_user.role != "admin":
        base_query = base_query.filter(DetectionEvent.user_id == current_user.id)

    critical = base_query.filter(DetectionEvent.risk_score >= 80).count()
    high = base_query.filter(DetectionEvent.risk_score >= 60, DetectionEvent.risk_score < 80).count()
    medium = base_query.filter(DetectionEvent.risk_score >= 47, DetectionEvent.risk_score < 60).count()
    low = base_query.filter(DetectionEvent.risk_score < 47).count()

    return {
        "labels": ["Critical", "High", "Medium", "Low"],
        "values": [critical, high, medium, low]
    }


# ============================================================
# RECENT EVENTS
# ============================================================

@app.get("/dashboard/recent")
def dashboard_recent(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    limit = max(1, min(limit, 100))

    base_query = db.query(DetectionEvent)
    if current_user.role != "admin":
        base_query = base_query.filter(DetectionEvent.user_id == current_user.id)

    events = (
        base_query
        .order_by(DetectionEvent.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "sender": event.sender,
            "receiver": event.receiver,
            "subject": event.subject,
            "label": event.label,
            "predicted_class": event.predicted_class,
            "phishing_probability": event.phishing_probability,
            "non_phishing_probability": event.non_phishing_probability,
            "risk_score": event.risk_score,
            "risk_level": get_risk_level(event.risk_score),
            "graph_neighbors": event.graph_neighbors
        }
        for event in events
    ]


# ============================================================
# DETECTION TIMELINE
# ============================================================

@app.get("/dashboard/timeline")
def dashboard_timeline(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hours = max(1, min(hours, 168))
    now = datetime.utcnow()
    start_time = now - timedelta(hours=hours)

    base_query = db.query(DetectionEvent).filter(DetectionEvent.timestamp >= start_time)
    if current_user.role != "admin":
        base_query = base_query.filter(DetectionEvent.user_id == current_user.id)

    events = base_query.order_by(DetectionEvent.timestamp.asc()).all()

    timeline = {}
    for i in range(hours):
        hour_time = start_time + timedelta(hours=i)
        hour_key = hour_time.strftime("%Y-%m-%d %H:00")
        timeline[hour_key] = {"hour": hour_key, "total": 0, "phishing": 0, "non_phishing": 0}

    for event in events:
        hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
        if hour_key not in timeline:
            timeline[hour_key] = {"hour": hour_key, "total": 0, "phishing": 0, "non_phishing": 0}
        timeline[hour_key]["total"] += 1
        if event.predicted_class == 1:
            timeline[hour_key]["phishing"] += 1
        else:
            timeline[hour_key]["non_phishing"] += 1

    return list(timeline.values())


# ==================================================
# EXTENSION MANAGEMENT
# ==================================================

@app.get("/extension/status")
def get_extension_status(current_user: User = Depends(get_current_active_user)):
    return EXTENSION_CONFIG

@app.post("/extension/toggle")
def toggle_extension(current_user: User = Depends(get_current_admin_user)):
    EXTENSION_CONFIG["enabled"] = not EXTENSION_CONFIG["enabled"]
    return EXTENSION_CONFIG

# ==================================================
# REPORTS
# ==================================================

@app.get("/reports/generate")
def generate_report(days: int = 7, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    start_time = datetime.utcnow() - timedelta(days=days)
    events = db.query(DetectionEvent).filter(DetectionEvent.timestamp >= start_time).all()
    
    total = len(events)
    phishing = sum(1 for e in events if e.predicted_class == 1)
    safe = total - phishing
    
    return {
        "period": f"Last {days} days",
        "total_scans": total,
        "phishing_detected": phishing,
        "safe_emails": safe,
        "detection_rate": round(phishing / total * 100, 2) if total > 0 else 0,
        "summary": "Report generated successfully."
    }

# ==================================================
# ADMIN CONSOLE
# ==================================================

@app.get("/admin/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    return db.query(User).all()


# ==================================================
# MODEL PERFORMANCE (ADMIN ONLY)
# ==================================================

@app.get("/model/performance")
def get_model_performance(current_user: User = Depends(get_current_admin_user)):
    """
    Returns verified model performance metrics derived from real dataset evaluations
    and training trajectory on CEAS-08. Only accessible by administrators.
    """
    data = get_performance_data()
    return data


@app.get("/model/performance/charts/{chart_name}")
def get_model_chart(
    chart_name: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Returns generated backend chart image output (PNG) for model evaluation.
    Only accessible by administrators.
    """
    normalized_name = chart_name.lower().replace("-", "_")
    if not normalized_name.endswith(".png"):
        normalized_name += ".png"

    chart_file = CHARTS_DIR / normalized_name
    test_eval_file = CHARTS_DIR.parent / "test_evaluation" / normalized_name

    if not chart_file.exists() and test_eval_file.exists():
        chart_file = test_eval_file
    elif not chart_file.exists():
        generate_all_charts()
        if not chart_file.exists() and test_eval_file.exists():
            chart_file = test_eval_file

    if not chart_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Chart '{chart_name}' not found. Available charts: loss_curve, accuracy_curve, confusion_matrix, roc_curve, threshold_analysis, sample_scaling, executive_dashboard"
        )

    return FileResponse(
        path=str(chart_file),
        media_type="image/png",
        filename=normalized_name
    )


@app.post("/model/performance/generate-charts")
def trigger_generate_charts(current_user: User = Depends(get_current_admin_user)):
    """
    Triggers regeneration of all backend performance chart outputs
    from current evaluation datasets and metrics. Only accessible by administrators.
    """
    generated = generate_all_charts()
    return {
        "status": "success",
        "message": "All backend model performance charts generated successfully.",
        "charts": generated
    }