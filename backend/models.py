from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Category(str, Enum):
    CLAIMS = "claims"
    BILLING = "billing"
    COVERAGE = "coverage"
    ENROLLMENT = "enrollment"
    PRIOR_AUTHORIZATION = "prior_authorization"
    APPEALS_GRIEVANCES = "appeals_grievances"
    PROVIDER_NETWORK = "provider_network"
    PHARMACY_BENEFITS = "pharmacy_benefits"
    MEMBER_SERVICES = "member_services"
    TECHNICAL_SUPPORT = "technical_support"
    HIPAA_COMPLIANCE = "hipaa_compliance"
    FRAUD = "fraud"
    OTHER = "other"


class Priority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Team(str, Enum):
    CLAIMS_PROCESSING = "claims_processing"
    MEMBER_SERVICES = "member_services"
    PROVIDER_RELATIONS = "provider_relations"
    BILLING_FINANCE = "billing_finance"
    UTILIZATION_MANAGEMENT = "utilization_management"
    APPEALS_GRIEVANCES = "appeals_grievances"
    PHARMACY_SERVICES = "pharmacy_services"
    ENROLLMENT_ELIGIBILITY = "enrollment_eligibility"
    COMPLIANCE_LEGAL = "compliance_legal"
    IT_SUPPORT = "it_support"
    FRAUD_INVESTIGATION = "fraud_investigation"


class ComplianceFlag(str, Enum):
    NONE = "none"
    HIPAA_REVIEW = "hipaa_review"
    STATE_MANDATE = "state_mandate"
    CMS_REGULATION = "cms_regulation"
    URGENT_CARE = "urgent_care"
    ACA_RELATED = "aca_related"


class TicketInput(BaseModel):
    title: str
    description: str
    member_id: Optional[str] = None
    plan_type: Optional[str] = None
    submitted_by: Optional[str] = None


class AgentResponseModel(BaseModel):
    """Response from a specialized agent"""
    agent_name: str
    action: str
    message: str
    confidence: float
    requires_human: bool = False
    data: Optional[dict] = None


class TriageResult(BaseModel):
    category: Category
    priority: Priority
    assigned_team: Team
    compliance_flag: ComplianceFlag
    suggested_response: str
    reasoning: str
    sla_hours: int
    confidence_score: float


class TriageResponse(BaseModel):
    success: bool
    ticket: TicketInput
    triage: Optional[TriageResult] = None
    agent_response: Optional[AgentResponseModel] = None
    error: Optional[str] = None
