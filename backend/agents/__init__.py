"""
HealthFirst Insurance AI Agents

This package contains specialized AI agents for handling
different types of health insurance member inquiries.

Available Agents:
- ClaimsAgent: Handles claims status, denials, EOB, reimbursement
- PriorAuthAgent: Handles prior authorization requests and status
- BenefitsAgent: Handles coverage questions and benefits explanations
- BillingAgent: Handles billing inquiries and payment issues
- MemberServicesAgent: Handles general member service requests
- AppealsGrievancesAgent: Handles appeals and grievances (requires human review)
- ProactiveOutreachAgent: Handles wellness programs and preventive care
"""

from .base_agent import (
    BaseAgent,
    AgentContext,
    AgentResponse,
    AgentAction,
    AgentOrchestrator
)
from .claims_agent import ClaimsAgent
from .prior_auth_agent import PriorAuthAgent
from .benefits_agent import BenefitsAgent
from .billing_agent import BillingAgent
from .member_services_agent import MemberServicesAgent
from .appeals_agent import AppealsGrievancesAgent
from .outreach_agent import ProactiveOutreachAgent

__all__ = [
    "BaseAgent",
    "AgentContext",
    "AgentResponse",
    "AgentAction",
    "AgentOrchestrator",
    "ClaimsAgent",
    "PriorAuthAgent",
    "BenefitsAgent",
    "BillingAgent",
    "MemberServicesAgent",
    "AppealsGrievancesAgent",
    "ProactiveOutreachAgent"
]


def create_agent_orchestrator() -> AgentOrchestrator:
    """
    Factory function to create a fully configured agent orchestrator
    with all available agents registered.
    """
    orchestrator = AgentOrchestrator()

    # Register specialized agents (order matters - first match wins)

    # High-priority specialized agents
    orchestrator.register_agent(AppealsGrievancesAgent())  # Appeals always need human review
    orchestrator.register_agent(PriorAuthAgent())  # Time-sensitive requests

    # Domain-specific agents
    orchestrator.register_agent(ClaimsAgent())
    orchestrator.register_agent(BillingAgent())
    orchestrator.register_agent(BenefitsAgent())
    orchestrator.register_agent(ProactiveOutreachAgent())

    # Default fallback agent for general inquiries
    orchestrator.register_agent(MemberServicesAgent(), is_default=True)

    return orchestrator
