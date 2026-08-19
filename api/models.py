from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime

from api.database import Base


class DetectionEvent(Base):

    __tablename__ = "detection_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    sender = Column(Text)
    receiver = Column(Text)
    subject = Column(Text)

    label = Column(String(30), nullable=False)

    predicted_class = Column(
        Integer,
        nullable=False
    )

    phishing_probability = Column(
        Float,
        nullable=False
    )

    non_phishing_probability = Column(
        Float,
        nullable=False
    )

    risk_score = Column(
        Float,
        nullable=False
    )

    graph_neighbors = Column(
        Integer,
        nullable=False
    )

    graph_edge_types = Column(Text)

    sender_entity = Column(Text)
    receiver_entity = Column(Text)

    domain_entities = Column(Text)