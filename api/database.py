from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker



DATABASE_URL = "sqlite:///./phishguard.db"


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

    Base.metadata.create_all(
        bind=engine
    )

    print(
        "Database initialized successfully."
    )


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()