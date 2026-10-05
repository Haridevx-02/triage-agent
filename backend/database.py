from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
import enum

DATABASE_URL = "sqlite+aiosqlite:///./healthfirst.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class PlanType(str, enum.Enum):
    PPO = "PPO"
    HMO = "HMO"
    EPO = "EPO"
    POS = "POS"
    HDHP = "HDHP"
    MEDICARE_ADVANTAGE = "Medicare Advantage"
    MEDICAID = "Medicaid"
    INDIVIDUAL = "Individual"
    GROUP = "Group"


class PolicyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    CANCELLED = "cancelled"


class PolicyHolder(Base):
    __tablename__ = "policy_holders"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    date_of_birth = Column(String(10))

    # Policy Details
    plan_type = Column(String(50), nullable=False)
    policy_number = Column(String(50))
    group_number = Column(String(50))
    policy_status = Column(String(20), default="active")
    effective_date = Column(String(10))
    termination_date = Column(String(10))

    # Coverage Details
    deductible = Column(Float, default=0)
    deductible_met = Column(Float, default=0)
    out_of_pocket_max = Column(Float, default=0)
    out_of_pocket_met = Column(Float, default=0)
    copay_primary = Column(Float, default=0)
    copay_specialist = Column(Float, default=0)
    copay_emergency = Column(Float, default=0)

    # Flags
    has_dental = Column(Integer, default=0)
    has_vision = Column(Integer, default=0)
    has_pharmacy = Column(Integer, default=1)
    prior_auth_required = Column(Integer, default=1)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inquiries = relationship("Inquiry", back_populates="policy_holder")


class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String(50), ForeignKey("policy_holders.member_id"), index=True)

    # Inquiry Details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    submitted_by = Column(String(255))

    # Triage Results
    category = Column(String(50))
    priority = Column(String(20))
    assigned_team = Column(String(50))
    compliance_flag = Column(String(50))
    suggested_response = Column(Text)
    reasoning = Column(Text)
    sla_hours = Column(Integer)
    confidence_score = Column(Float)

    # Status Tracking
    status = Column(String(20), default="open")  # open, in_progress, resolved, closed
    resolution = Column(Text)
    resolved_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    policy_holder = relationship("PolicyHolder", back_populates="inquiries")


async def init_db():
    """Initialize the database and create tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get a database session."""
    async with async_session() as session:
        yield session
