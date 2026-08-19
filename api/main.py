from api.models import DetectionEvent
from pydantic import BaseModel
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy.orm import Session
from api.database import (
    get_db,
    init_database
)
from fastapi.middleware.cors import CORSMiddleware

from api.predictor import (
    PhishGuardPredictor
)
from fastapi import FastAPI, Depends

import json





import json


app = FastAPI(
    title="PhishGuard AI",
    description=(
        "DistilBERT + Graph Attention "
        "Network Phishing Detection API"
    ),
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Initialize database
# --------------------------------------------------

init_database()


# --------------------------------------------------
# Load model once
# --------------------------------------------------

predictor = PhishGuardPredictor()


# --------------------------------------------------
# Request schema
# --------------------------------------------------

class EmailRequest(BaseModel):

    sender: str

    receiver: str

    subject: str

    body: str


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():

    return {

        "application": "PhishGuard AI",

        "status": "running",

        "model":
            "DistilBERT + Graph Attention Network"

    }


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "model":
            "DistilBERT + GAT"

    }


# --------------------------------------------------
# Prediction
# --------------------------------------------------

@app.post("/predict")
def predict_email(
    request: EmailRequest,
    db: Session = Depends(get_db)
):

    # ========================================================
    # 1. MODEL PREDICTION
    # ========================================================

    result = predictor.predict(
        sender=request.sender,
        receiver=request.receiver,
        subject=request.subject,
        body=request.body
    )

    # ========================================================
    # 2. SAVE DETECTION EVENT
    # ========================================================

    event = DetectionEvent(

        sender=request.sender,

        receiver=request.receiver,

        subject=request.subject,

        label=result["label"],

        predicted_class=result[
            "predicted_class"
        ],

        phishing_probability=result[
            "phishing_probability"
        ],

        non_phishing_probability=result[
            "non_phishing_probability"
        ],

        risk_score=result[
            "risk_score"
        ],

        graph_neighbors=result[
            "graph_neighbors"
        ],

        graph_edge_types=json.dumps(
            result["graph_edge_types"]
        ),

        sender_entity=result[
            "sender_entity"
        ],

        receiver_entity=result[
            "receiver_entity"
        ],

        domain_entities=json.dumps(
            result["domain_entities"]
        )
    )

    # ========================================================
    # 3. DATABASE COMMIT
    # ========================================================

    db.add(event)

    db.commit()

    db.refresh(event)

    # ========================================================
    # 4. ADD DATABASE METADATA TO RESPONSE
    # ========================================================

    result["event_id"] = event.id

    result["timestamp"] = (
        event.timestamp.isoformat()
    )

    # ========================================================
    # 5. RETURN FINAL RESPONSE
    # ========================================================

    return result


    # ----------------------------------------------
    # Add event ID to API response
    # ----------------------------------------------

  

@app.get("/events")
def get_events(
    limit: int = 100,
    db: Session = Depends(get_db)
):

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    events = (
        db.query(DetectionEvent)
        .order_by(
            DetectionEvent.timestamp.desc()
        )
        .limit(limit)
        .all()
    )

    def get_risk_level(score):

        if score >= 80:
            return "CRITICAL"

        if score >= 60:
            return "HIGH"

        if score >= 47:
            return "MEDIUM"

        return "LOW"

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

    db: Session = Depends(get_db)

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
# SOC DASHBOARD ENDPOINTS
# ============================================================
# ============================================================
# SOC DASHBOARD ENDPOINTS
# ============================================================
@app.get("/dashboard/overview")
def dashboard_overview(
    db: Session = Depends(get_db)
):

    total_events = (
        db.query(DetectionEvent)
        .count()
    )

    phishing_events = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.predicted_class == 1
        )
        .count()
    )

    non_phishing_events = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.predicted_class == 0
        )
        .count()
    )

    # --------------------------------------------------------
    # Risk distribution
    # --------------------------------------------------------

    critical_events = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.risk_score >= 80
        )
        .count()
    )

    high_events = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.risk_score >= 60,
            DetectionEvent.risk_score < 80
        )
        .count()
    )

    medium_events = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.risk_score >= 47,
            DetectionEvent.risk_score < 60
        )
        .count()
    )

    low_events = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.risk_score < 47
        )
        .count()
    )

    # --------------------------------------------------------
    # Average risk
    # --------------------------------------------------------

    risk_values = (
        db.query(
            DetectionEvent.risk_score
        )
        .all()
    )

    if risk_values:

        average_risk_score = (
            sum(row[0] for row in risk_values)
            / len(risk_values)
        )

    else:

        average_risk_score = 0.0

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "total_events":
            total_events,

        "phishing_events":
            phishing_events,

        "non_phishing_events":
            non_phishing_events,

        "phishing_percentage":
            round(
                phishing_events / total_events * 100,
                2
            )
            if total_events > 0
            else 0.0,

        "non_phishing_percentage":
            round(
                non_phishing_events / total_events * 100,
                2
            )
            if total_events > 0
            else 0.0,

        "average_risk_score":
            round(
                average_risk_score,
                2
            ),

        "risk_distribution": {

            "critical":
                critical_events,

            "high":
                high_events,

            "medium":
                medium_events,

            "low":
                low_events
        }
    }
# ============================================================
# PHISHING VS NON-PHISHING DISTRIBUTION
# ============================================================

@app.get("/dashboard/distribution")
def dashboard_distribution(
    db: Session = Depends(get_db)
):

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

    return {

        "labels": [
            "Phishing",
            "Non-Phishing"
        ],

        "values": [
            phishing,
            non_phishing
        ]
    }


# ============================================================
# RISK DISTRIBUTION
# ============================================================

@app.get("/dashboard/risk-distribution")
def dashboard_risk_distribution(
    db: Session = Depends(get_db)
):

    critical = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.risk_score >= 80
        )
        .count()
    )

    high = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.risk_score >= 60,
            DetectionEvent.risk_score < 80
        )
        .count()
    )

    medium = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.risk_score >= 47,
            DetectionEvent.risk_score < 60
        )
        .count()
    )

    low = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.risk_score < 47
        )
        .count()
    )

    return {

        "labels": [
            "Critical",
            "High",
            "Medium",
            "Low"
        ],

        "values": [
            critical,
            high,
            medium,
            low
        ]
    }


# ============================================================
# RECENT EVENTS
# ============================================================

@app.get("/dashboard/recent")
def dashboard_recent(
    limit: int = 10,
    db: Session = Depends(get_db)
):

    limit = max(1, min(limit, 100))

    events = (
        db.query(DetectionEvent)
        .order_by(
            DetectionEvent.timestamp.desc()
        )
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

            "graph_neighbors":
                event.graph_neighbors
        }

        for event in events
    ]


# ============================================================
# DETECTION TIMELINE
# ============================================================

@app.get("/dashboard/timeline")
def dashboard_timeline(
    hours: int = 24,
    db: Session = Depends(get_db)
):

    hours = max(1, min(hours, 168))

    now = datetime.utcnow()

    start_time = (
        now - timedelta(hours=hours)
    )

    events = (
        db.query(DetectionEvent)
        .filter(
            DetectionEvent.timestamp >= start_time
        )
        .order_by(
            DetectionEvent.timestamp.asc()
        )
        .all()
    )

    timeline = {}

    # --------------------------------------------------------
    # Create every requested hour
    # --------------------------------------------------------

    for i in range(hours):

        hour_time = (
            start_time +
            timedelta(hours=i)
        )

        hour_key = hour_time.strftime(
            "%Y-%m-%d %H:00"
        )

        timeline[hour_key] = {

            "hour": hour_key,

            "total": 0,

            "phishing": 0,

            "non_phishing": 0
        }

    # --------------------------------------------------------
    # Add real database events
    # --------------------------------------------------------

    for event in events:

        hour_key = event.timestamp.strftime(
            "%Y-%m-%d %H:00"
        )

        if hour_key not in timeline:

            timeline[hour_key] = {

                "hour": hour_key,

                "total": 0,

                "phishing": 0,

                "non_phishing": 0
            }

        timeline[hour_key]["total"] += 1

        if event.predicted_class == 1:

            timeline[hour_key]["phishing"] += 1

        else:

            timeline[hour_key]["non_phishing"] += 1

    return list(
        timeline.values()
    )