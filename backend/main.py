from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
import os
import socket


def find_available_port(host: str, preferred_port: int, max_attempts: int = 25) -> int:
    """Return the first free port starting from the preferred value."""
    for port in range(preferred_port, preferred_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free port found between {preferred_port} and {preferred_port + max_attempts - 1}.")


HOST = os.getenv("HOST", "127.0.0.1")
PREFERRED_PORT = int(os.getenv("PORT", "8001"))
PORT = find_available_port(HOST, PREFERRED_PORT)

from models import TicketInput, TriageResponse
from triage_service import triage_ticket
from database import init_db
from chat_service import ChatRequest, ChatResponse, ChatMessage, chat_with_agent
import db_service


# Pydantic models for API
class PolicyHolderCreate(BaseModel):
    member_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    plan_type: str
    policy_number: Optional[str] = None
    group_number: Optional[str] = None
    policy_status: str = "active"
    effective_date: Optional[str] = None
    termination_date: Optional[str] = None
    deductible: float = 0
    deductible_met: float = 0
    out_of_pocket_max: float = 0
    out_of_pocket_met: float = 0
    copay_primary: float = 30
    copay_specialist: float = 50
    copay_emergency: float = 250
    has_dental: int = 0
    has_vision: int = 0
    has_pharmacy: int = 1
    prior_auth_required: int = 1


class PolicyHolderResponse(BaseModel):
    id: int
    member_id: str
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    plan_type: str
    policy_status: str
    deductible: float
    deductible_met: float
    out_of_pocket_max: float
    out_of_pocket_met: float

    class Config:
        from_attributes = True


class InquiryResponse(BaseModel):
    id: int
    member_id: Optional[str]
    title: str
    description: str
    category: Optional[str]
    priority: Optional[str]
    assigned_team: Optional[str]
    status: str
    created_at: Optional[str]

    class Config:
        from_attributes = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="CarePilot AI - Member Services Triage API",
    description="AI-powered member services triage system with policy holder context and routed agent responses",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def root():
    """Serve the frontend."""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "HealthFirst Insurance Triage API", "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "healthfirst-triage"}


# ============== Triage Endpoints ==============

@app.post("/api/triage", response_model=TriageResponse)
async def triage_endpoint(ticket: TicketInput):
    """
    Submit a ticket for AI-powered triage.

    If member_id is provided and exists in the database, the AI will use
    the member's policy details and inquiry history for context.
    """
    result = await triage_ticket(ticket)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result


# ============== Policy Holder Endpoints ==============

@app.post("/api/members", response_model=dict)
async def create_member(member: PolicyHolderCreate):
    """Create a new policy holder."""
    try:
        existing = await db_service.get_policy_holder(member.member_id)
        if existing:
            raise HTTPException(status_code=400, detail="Member ID already exists")

        policy_holder = await db_service.create_policy_holder(member.model_dump())
        return {"success": True, "member_id": policy_holder.member_id, "message": "Member created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/members/{member_id}")
async def get_member(member_id: str):
    """Get policy holder details and inquiry history."""
    data = await db_service.get_policy_holder_with_history(member_id)
    if not data:
        raise HTTPException(status_code=404, detail="Member not found")

    ph = data["policy_holder"]
    inquiries = data["recent_inquiries"]

    return {
        "member": {
            "member_id": ph.member_id,
            "first_name": ph.first_name,
            "last_name": ph.last_name,
            "email": ph.email,
            "phone": ph.phone,
            "plan_type": ph.plan_type,
            "policy_status": ph.policy_status,
            "effective_date": ph.effective_date,
            "deductible": ph.deductible,
            "deductible_met": ph.deductible_met,
            "out_of_pocket_max": ph.out_of_pocket_max,
            "out_of_pocket_met": ph.out_of_pocket_met,
            "copay_primary": ph.copay_primary,
            "copay_specialist": ph.copay_specialist,
            "copay_emergency": ph.copay_emergency,
            "has_dental": ph.has_dental,
            "has_vision": ph.has_vision,
            "has_pharmacy": ph.has_pharmacy
        },
        "inquiry_count": len(inquiries),
        "recent_inquiries": [
            {
                "id": inq.id,
                "title": inq.title,
                "category": inq.category,
                "priority": inq.priority,
                "status": inq.status,
                "created_at": inq.created_at.isoformat() if inq.created_at else None
            }
            for inq in inquiries
        ]
    }


@app.get("/api/members")
async def list_members(search: Optional[str] = None):
    """List all policy holders or search by name/member ID."""
    if search:
        members = await db_service.search_policy_holders(search)
    else:
        members = await db_service.get_all_policy_holders()

    return {
        "count": len(members),
        "members": [
            {
                "member_id": m.member_id,
                "first_name": m.first_name,
                "last_name": m.last_name,
                "plan_type": m.plan_type,
                "policy_status": m.policy_status
            }
            for m in members
        ]
    }


@app.put("/api/members/{member_id}")
async def update_member(member_id: str, updates: dict):
    """Update policy holder details."""
    policy_holder = await db_service.update_policy_holder(member_id, updates)
    if not policy_holder:
        raise HTTPException(status_code=404, detail="Member not found")

    return {"success": True, "message": "Member updated successfully"}


@app.get("/api/members/{member_id}/inquiries")
async def get_member_inquiries(member_id: str):
    """Get all inquiries for a member."""
    inquiries = await db_service.get_member_inquiry_history(member_id)

    return {
        "member_id": member_id,
        "count": len(inquiries),
        "inquiries": [
            {
                "id": inq.id,
                "title": inq.title,
                "description": inq.description[:200] + "..." if len(inq.description) > 200 else inq.description,
                "category": inq.category,
                "priority": inq.priority,
                "assigned_team": inq.assigned_team,
                "compliance_flag": inq.compliance_flag,
                "status": inq.status,
                "created_at": inq.created_at.isoformat() if inq.created_at else None
            }
            for inq in inquiries
        ]
    }


# ============== Chat Endpoint ==============

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat with an AI agent for follow-up questions.

    Send a message and conversation history to continue the conversation.
    The agent will use member context if member_id is provided.
    """
    # If member_id provided, fetch context
    if request.member_id and not request.context:
        member_data = await db_service.get_policy_holder_with_history(request.member_id)
        if member_data:
            ph = member_data["policy_holder"]
            request.context = {
                "member_id": ph.member_id,
                "member_name": f"{ph.first_name} {ph.last_name}",
                "plan_type": ph.plan_type,
                "deductible": ph.deductible,
                "deductible_met": ph.deductible_met,
                "copay_primary": ph.copay_primary,
                "copay_specialist": ph.copay_specialist
            }

    result = await chat_with_agent(request)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result


# ============== Seed Data Endpoint ==============

@app.post("/api/seed-demo-data")
async def seed_demo_data():
    """Seed the database with demo policy holders for testing."""
    demo_members = [
        {
            "member_id": "HF100001",
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@email.com",
            "phone": "555-123-4567",
            "date_of_birth": "1985-03-15",
            "plan_type": "PPO",
            "policy_number": "POL-2024-001",
            "group_number": "GRP-ACME-100",
            "policy_status": "active",
            "effective_date": "2024-01-01",
            "deductible": 1500.00,
            "deductible_met": 750.00,
            "out_of_pocket_max": 6000.00,
            "out_of_pocket_met": 1200.00,
            "copay_primary": 25.00,
            "copay_specialist": 50.00,
            "copay_emergency": 250.00,
            "has_dental": 1,
            "has_vision": 1,
            "has_pharmacy": 1,
            "prior_auth_required": 1
        },
        {
            "member_id": "HF100002",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah.j@email.com",
            "phone": "555-987-6543",
            "date_of_birth": "1972-08-22",
            "plan_type": "Medicare Advantage",
            "policy_number": "POL-2024-002",
            "policy_status": "active",
            "effective_date": "2024-01-01",
            "deductible": 0,
            "deductible_met": 0,
            "out_of_pocket_max": 3500.00,
            "out_of_pocket_met": 500.00,
            "copay_primary": 0,
            "copay_specialist": 20.00,
            "copay_emergency": 90.00,
            "has_dental": 1,
            "has_vision": 1,
            "has_pharmacy": 1,
            "prior_auth_required": 1
        },
        {
            "member_id": "HF100003",
            "first_name": "Michael",
            "last_name": "Williams",
            "email": "m.williams@email.com",
            "phone": "555-456-7890",
            "date_of_birth": "1990-11-30",
            "plan_type": "HDHP",
            "policy_number": "POL-2024-003",
            "group_number": "GRP-TECH-200",
            "policy_status": "active",
            "effective_date": "2024-01-01",
            "deductible": 3000.00,
            "deductible_met": 3000.00,
            "out_of_pocket_max": 7000.00,
            "out_of_pocket_met": 4500.00,
            "copay_primary": 0,
            "copay_specialist": 0,
            "copay_emergency": 0,
            "has_dental": 0,
            "has_vision": 0,
            "has_pharmacy": 1,
            "prior_auth_required": 1
        },
        {
            "member_id": "HF100004",
            "first_name": "Emily",
            "last_name": "Davis",
            "email": "emily.davis@email.com",
            "phone": "555-321-0987",
            "date_of_birth": "1968-05-10",
            "plan_type": "HMO",
            "policy_number": "POL-2024-004",
            "policy_status": "active",
            "effective_date": "2024-01-01",
            "deductible": 500.00,
            "deductible_met": 500.00,
            "out_of_pocket_max": 4000.00,
            "out_of_pocket_met": 2000.00,
            "copay_primary": 15.00,
            "copay_specialist": 35.00,
            "copay_emergency": 150.00,
            "has_dental": 1,
            "has_vision": 0,
            "has_pharmacy": 1,
            "prior_auth_required": 1
        }
    ]

    created = 0
    skipped = 0

    for member_data in demo_members:
        existing = await db_service.get_policy_holder(member_data["member_id"])
        if existing:
            skipped += 1
            continue

        await db_service.create_policy_holder(member_data)
        created += 1

    return {
        "success": True,
        "message": f"Demo data seeded: {created} created, {skipped} skipped (already exist)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
