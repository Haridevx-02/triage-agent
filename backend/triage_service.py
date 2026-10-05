from models import (
    TicketInput,
    TriageResult,
    TriageResponse,
    AgentResponseModel,
    Category,
    Priority,
    Team,
    ComplianceFlag
)
from grok_service import call_groq_api
from db_service import get_policy_holder_with_history, save_inquiry, format_policy_context
from rag_service import build_rag_context
from agents import create_agent_orchestrator, AgentContext


# Initialize the agent orchestrator
agent_orchestrator = create_agent_orchestrator()


def get_agent_name_from_category(category: str) -> str:
    """Map category to agent name for display purposes"""
    agent_map = {
        "claims": "Claims Agent",
        "billing": "Billing Agent",
        "coverage": "Benefits Agent",
        "enrollment": "Member Services Agent",
        "prior_authorization": "Prior Authorization Agent",
        "appeals_grievances": "Appeals & Grievances Agent",
        "provider_network": "Benefits Agent",
        "pharmacy_benefits": "Benefits Agent",
        "member_services": "Member Services Agent",
        "technical_support": "Member Services Agent",
        "hipaa_compliance": "Appeals & Grievances Agent",
        "fraud": "Appeals & Grievances Agent",
        "other": "Member Services Agent"
    }
    return agent_map.get(category, "Member Services Agent")


async def triage_ticket(ticket: TicketInput) -> TriageResponse:
    """Process a health insurance ticket through the AI triage system."""

    try:
        # Get policy holder details and history if member_id provided
        policy_context = ""
        policy_details = None
        inquiry_history = []

        if ticket.member_id:
            member_data = await get_policy_holder_with_history(ticket.member_id)
            if member_data:
                policy_holder = member_data["policy_holder"]
                policy_context = format_policy_context(
                    policy_holder,
                    member_data["recent_inquiries"]
                )
                # Extract policy details for agent context
                policy_details = {
                    "member_id": policy_holder.member_id,
                    "first_name": policy_holder.first_name,
                    "last_name": policy_holder.last_name,
                    "plan_type": policy_holder.plan_type,
                    "policy_status": policy_holder.policy_status,
                    "deductible": policy_holder.deductible,
                    "deductible_met": policy_holder.deductible_met,
                    "out_of_pocket_max": policy_holder.out_of_pocket_max,
                    "out_of_pocket_met": policy_holder.out_of_pocket_met,
                    "copay_primary": policy_holder.copay_primary,
                    "copay_specialist": policy_holder.copay_specialist,
                    "copay_emergency": policy_holder.copay_emergency,
                    "has_dental": policy_holder.has_dental,
                    "has_vision": policy_holder.has_vision,
                    "has_pharmacy": policy_holder.has_pharmacy,
                    "date_of_birth": policy_holder.date_of_birth,
                    "gender": getattr(policy_holder, 'gender', None)
                }
                # Format inquiry history for agents
                inquiry_history = [
                    {
                        "category": inq.category,
                        "priority": inq.priority,
                        "title": inq.title,
                        "status": inq.status
                    }
                    for inq in member_data["recent_inquiries"]
                ]

        # Add retrieved knowledge to the prompt so the model answers using both
        # member-specific context and the local insurance knowledge base.
        rag_context = build_rag_context(
            f"{ticket.title} {ticket.description}",
            member_context=policy_context,
            top_k=3,
        )

        result = await call_groq_api(
            title=ticket.title,
            description=ticket.description,
            member_id=ticket.member_id or "Not Provided",
            plan_type=ticket.plan_type or "Not Specified",
            submitted_by=ticket.submitted_by or "Unknown",
            policy_context=rag_context
        )

        # Map the response to our models
        triage_result = TriageResult(
            category=Category(result["category"]),
            priority=Priority(result["priority"]),
            assigned_team=Team(result["assigned_team"]),
            compliance_flag=ComplianceFlag(result["compliance_flag"]),
            suggested_response=result["suggested_response"],
            reasoning=result["reasoning"],
            sla_hours=int(result["sla_hours"]),
            confidence_score=float(result["confidence_score"])
        )

        # Route to specialized agent for detailed response
        agent_response = None
        try:
            # Build compliance flags list
            compliance_flags = []
            if result["compliance_flag"] != "none":
                compliance_flags.append(result["compliance_flag"])

            # Create agent context
            agent_context = AgentContext(
                member_id=ticket.member_id,
                inquiry_title=ticket.title,
                inquiry_description=ticket.description,
                policy_details=policy_details,
                inquiry_history=inquiry_history,
                current_category=result["category"],
                priority=result["priority"],
                compliance_flags=compliance_flags
            )

            # Route to appropriate agent
            agent_result = await agent_orchestrator.route(agent_context)

            # Format agent response for API
            agent_response = AgentResponseModel(
                agent_name=get_agent_name_from_category(result["category"]),
                action=agent_result.action.value,
                message=agent_result.message,
                confidence=agent_result.confidence,
                requires_human=agent_result.requires_human,
                data=agent_result.data
            )

        except Exception as agent_error:
            # If agent processing fails, continue without agent response
            import traceback
            print(f"Agent processing error: {agent_error}")
            traceback.print_exc()
            agent_response = None

        # Save inquiry to database
        await save_inquiry(
            member_id=ticket.member_id,
            ticket_data={
                "title": ticket.title,
                "description": ticket.description,
                "submitted_by": ticket.submitted_by
            },
            triage_data={
                "category": result["category"],
                "priority": result["priority"],
                "assigned_team": result["assigned_team"],
                "compliance_flag": result["compliance_flag"],
                "suggested_response": result["suggested_response"],
                "reasoning": result["reasoning"],
                "sla_hours": result["sla_hours"],
                "confidence_score": result["confidence_score"]
            }
        )

        return TriageResponse(
            success=True,
            ticket=ticket,
            triage=triage_result,
            agent_response=agent_response
        )

    except ValueError as e:
        return TriageResponse(
            success=False,
            ticket=ticket,
            error=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        return TriageResponse(
            success=False,
            ticket=ticket,
            error=f"Triage failed: {str(e)}"
        )
