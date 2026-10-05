from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database import PolicyHolder, Inquiry, async_session
from typing import Optional, List
from datetime import datetime


async def get_policy_holder(member_id: str) -> Optional[PolicyHolder]:
    """Get a policy holder by member ID."""
    async with async_session() as session:
        result = await session.execute(
            select(PolicyHolder).where(PolicyHolder.member_id == member_id)
        )
        return result.scalar_one_or_none()


async def get_policy_holder_with_history(member_id: str) -> dict:
    """Get policy holder details along with recent inquiry history."""
    async with async_session() as session:
        # Get policy holder
        result = await session.execute(
            select(PolicyHolder).where(PolicyHolder.member_id == member_id)
        )
        policy_holder = result.scalar_one_or_none()

        if not policy_holder:
            return None

        # Get recent inquiries (last 10)
        inquiries_result = await session.execute(
            select(Inquiry)
            .where(Inquiry.member_id == member_id)
            .order_by(desc(Inquiry.created_at))
            .limit(10)
        )
        inquiries = inquiries_result.scalars().all()

        return {
            "policy_holder": policy_holder,
            "recent_inquiries": inquiries
        }


async def create_policy_holder(data: dict) -> PolicyHolder:
    """Create a new policy holder."""
    async with async_session() as session:
        policy_holder = PolicyHolder(**data)
        session.add(policy_holder)
        await session.commit()
        await session.refresh(policy_holder)
        return policy_holder


async def update_policy_holder(member_id: str, data: dict) -> Optional[PolicyHolder]:
    """Update a policy holder."""
    async with async_session() as session:
        result = await session.execute(
            select(PolicyHolder).where(PolicyHolder.member_id == member_id)
        )
        policy_holder = result.scalar_one_or_none()

        if not policy_holder:
            return None

        for key, value in data.items():
            if hasattr(policy_holder, key):
                setattr(policy_holder, key, value)

        policy_holder.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(policy_holder)
        return policy_holder


async def save_inquiry(member_id: Optional[str], ticket_data: dict, triage_data: dict) -> Inquiry:
    """Save an inquiry to the database."""
    async with async_session() as session:
        inquiry = Inquiry(
            member_id=member_id,
            title=ticket_data.get("title"),
            description=ticket_data.get("description"),
            submitted_by=ticket_data.get("submitted_by"),
            category=triage_data.get("category"),
            priority=triage_data.get("priority"),
            assigned_team=triage_data.get("assigned_team"),
            compliance_flag=triage_data.get("compliance_flag"),
            suggested_response=triage_data.get("suggested_response"),
            reasoning=triage_data.get("reasoning"),
            sla_hours=triage_data.get("sla_hours"),
            confidence_score=triage_data.get("confidence_score"),
            status="open"
        )
        session.add(inquiry)
        await session.commit()
        await session.refresh(inquiry)
        return inquiry


async def get_member_inquiry_history(member_id: str) -> List[Inquiry]:
    """Get all inquiries for a member."""
    async with async_session() as session:
        result = await session.execute(
            select(Inquiry)
            .where(Inquiry.member_id == member_id)
            .order_by(desc(Inquiry.created_at))
        )
        return result.scalars().all()


async def get_all_policy_holders() -> List[PolicyHolder]:
    """Get all policy holders."""
    async with async_session() as session:
        result = await session.execute(
            select(PolicyHolder).order_by(PolicyHolder.last_name)
        )
        return result.scalars().all()


async def search_policy_holders(query: str) -> List[PolicyHolder]:
    """Search policy holders by name or member ID."""
    async with async_session() as session:
        search_term = f"%{query}%"
        result = await session.execute(
            select(PolicyHolder).where(
                (PolicyHolder.member_id.ilike(search_term)) |
                (PolicyHolder.first_name.ilike(search_term)) |
                (PolicyHolder.last_name.ilike(search_term)) |
                (PolicyHolder.email.ilike(search_term))
            )
        )
        return result.scalars().all()


def format_policy_context(policy_holder: PolicyHolder, inquiries: List[Inquiry]) -> str:
    """Format policy holder info and history for AI context."""
    context = f"""
MEMBER POLICY DETAILS:
- Member ID: {policy_holder.member_id}
- Name: {policy_holder.first_name} {policy_holder.last_name}
- Plan Type: {policy_holder.plan_type}
- Policy Status: {policy_holder.policy_status}
- Effective Date: {policy_holder.effective_date or 'N/A'}

COVERAGE DETAILS:
- Deductible: ${policy_holder.deductible:,.2f} (Met: ${policy_holder.deductible_met:,.2f})
- Out-of-Pocket Max: ${policy_holder.out_of_pocket_max:,.2f} (Met: ${policy_holder.out_of_pocket_met:,.2f})
- Primary Care Copay: ${policy_holder.copay_primary:,.2f}
- Specialist Copay: ${policy_holder.copay_specialist:,.2f}
- Emergency Copay: ${policy_holder.copay_emergency:,.2f}
- Pharmacy Benefits: {'Yes' if policy_holder.has_pharmacy else 'No'}
- Dental Coverage: {'Yes' if policy_holder.has_dental else 'No'}
- Vision Coverage: {'Yes' if policy_holder.has_vision else 'No'}
- Prior Auth Required: {'Yes' if policy_holder.prior_auth_required else 'No'}
"""

    if inquiries:
        context += "\nRECENT INQUIRY HISTORY:\n"
        for i, inq in enumerate(inquiries[:5], 1):
            context += f"""
{i}. [{inq.created_at.strftime('%Y-%m-%d') if inq.created_at else 'N/A'}] {inq.title}
   Category: {inq.category} | Priority: {inq.priority} | Status: {inq.status}
   Summary: {inq.description[:100]}...
"""

    return context
