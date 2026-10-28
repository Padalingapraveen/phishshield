import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./phishguard.db")


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def init_database():
    from api.models import User
    from api.auth import get_password_hash
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Add user_id column safely if it doesn't exist
        try:
            db.execute(text("ALTER TABLE detection_events ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            db.commit()
            print("Added user_id column to detection_events.")
        except Exception:
            db.rollback()

        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_password = os.getenv("ADMIN_PASSWORD")
            if not admin_password:
                raise RuntimeError("ADMIN_PASSWORD must be set in the environment for first-time administrator provisioning.")
            new_admin = User(
                username=admin_username,
                hashed_password=get_password_hash(admin_password),
                role="admin"
            )
            db.add(new_admin)
            db.commit()
            print(f"Administrator provisioned (username: {admin_username})")
    finally:
        db.close()
        
    print("Database initialized successfully.")


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()