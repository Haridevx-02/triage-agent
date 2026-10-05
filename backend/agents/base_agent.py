"""
Base Agent Architecture for Health Insurance Ticket Triage System

This module provides the foundation for building specialized AI agents
that can handle different types of health insurance inquiries autonomously.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class AgentAction(Enum):
    """Actions an agent can take"""
    RESPOND = "respond"              # Send response to member
    ESCALATE = "escalate"            # Escalate to human agent
    TRANSFER = "transfer"            # Transfer to another agent
    LOOKUP = "lookup"                # Look up information
    UPDATE = "update"                # Update records
    CREATE_TASK = "create_task"      # Create follow-up task
    REQUEST_INFO = "request_info"    # Request more information
    APPROVE = "approve"              # Approve a request
    DENY = "deny"                    # Deny a request


@dataclass
class AgentContext:
    """Context passed to agents for decision making"""
    member_id: Optional[str]
    inquiry_title: str
    inquiry_description: str
    policy_details: Optional[Dict[str, Any]]
    inquiry_history: List[Dict[str, Any]]
    current_category: str
    priority: str
    compliance_flags: List[str]


@dataclass
class AgentResponse:
    """Response from an agent"""
    action: AgentAction
    message: str
    data: Optional[Dict[str, Any]] = None
    next_agent: Optional[str] = None
    requires_human: bool = False
    confidence: float = 0.0


class BaseAgent(ABC):
    """
    Base class for all health insurance agents.

    Each specialized agent inherits from this class and implements
    the process() method to handle specific types of inquiries.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.capabilities: List[str] = []

    @abstractmethod
    async def can_handle(self, context: AgentContext) -> bool:
        """Determine if this agent can handle the given inquiry"""
        pass

    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResponse:
        """Process the inquiry and return a response"""
        pass

    async def validate_compliance(self, context: AgentContext) -> List[str]:
        """Check for compliance issues that need attention"""
        issues = []

        # Check for HIPAA concerns
        if "hipaa_review" in context.compliance_flags:
            issues.append("HIPAA review required before proceeding")

        # Check for CMS regulations (Medicare/Medicaid)
        if context.policy_details:
            plan_type = context.policy_details.get("plan_type", "")
            if "Medicare" in plan_type or "Medicaid" in plan_type:
                issues.append("CMS regulations apply - verify compliance")

        # Check for urgent care requirements
        if context.priority == "urgent":
            issues.append("Urgent priority - expedited handling required")

        return issues

    def should_escalate(self, context: AgentContext) -> bool:
        """Determine if the inquiry should be escalated to a human"""
        # Escalate if multiple previous inquiries on same topic
        similar_inquiries = [
            inq for inq in context.inquiry_history
            if inq.get("category") == context.current_category
        ]
        if len(similar_inquiries) >= 3:
            return True

        # Escalate appeals and grievances by default
        if context.current_category in ["appeals_grievances", "fraud"]:
            return True

        return False


class AgentOrchestrator:
    """
    Orchestrates multiple agents and routes inquiries to the appropriate agent.
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.default_agent: Optional[str] = None

    def register_agent(self, agent: BaseAgent, is_default: bool = False):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        if is_default:
            self.default_agent = agent.name

    async def route(self, context: AgentContext) -> AgentResponse:
        """Route an inquiry to the appropriate agent"""

        # Find the best agent for this inquiry
        for name, agent in self.agents.items():
            if await agent.can_handle(context):
                response = await agent.process(context)

                # If agent wants to transfer, route to next agent
                if response.action == AgentAction.TRANSFER and response.next_agent:
                    next_agent = self.agents.get(response.next_agent)
                    if next_agent:
                        return await next_agent.process(context)

                return response

        # Fall back to default agent
        if self.default_agent:
            return await self.agents[self.default_agent].process(context)

        # No agent available
        return AgentResponse(
            action=AgentAction.ESCALATE,
            message="Unable to process automatically. Escalating to human agent.",
            requires_human=True,
            confidence=0.0
        )
