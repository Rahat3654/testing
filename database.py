import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DATE
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

# load local dev.env only if it exists (safe for local development)
if os.path.exists("dev.env"):
    load_dotenv("dev.env")

database_url = os.getenv("DATABASE_URL")
if database_url:
    # Some platforms provide URLs starting with postgres:// — SQLAlchemy + psycopg2 works better with postgresql+psycopg2://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    # If your provider requires ssl, enable it here (psycopg2)
    engine = create_engine(database_url, connect_args={"sslmode": "require"})
else:
    # Fallback to in-memory SQLite for CI/tests when DATABASE_URL is not set
    print("DATABASE_URL not set, using in-memory SQLite (CI/test mode)")
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    reference = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    Username = Column(String, unique=True, index=True)
    Password = Column(String, index=True)
    Name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    is_verified = Column(Boolean, default=False)
    dob = Column(DATE, index=True)
    Address = Column(String, nullable=True)
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_reference = Column(UUID(as_uuid=True), ForeignKey("users.reference"), nullable=False)
    secret = Column(String(32), nullable=True)
    user = relationship("User", back_populates="profile")
