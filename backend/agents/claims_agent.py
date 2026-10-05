"""
Claims Processing Agent

Handles claim status inquiries, claim denials, EOB questions,
and reimbursement issues autonomously.
"""

from .base_agent import BaseAgent, AgentContext, AgentResponse, AgentAction
from typing import Dict, Any


class ClaimsAgent(BaseAgent):
    """
    Specialized agent for handling claims-related inquiries.

    Capabilities:
    - Check claim status
    - Explain claim denials
    - Clarify EOB (Explanation of Benefits)
    - Process reimbursement questions
    - Identify missing documentation
    """

    def __init__(self):
        super().__init__(
            name="claims_agent",
            description="Handles claims status, denials, EOB, and reimbursement inquiries"
        )
        self.capabilities = [
            "claim_status_check",
            "denial_explanation",
            "eob_clarification",
            "reimbursement_calculation",
            "missing_docs_identification"
        ]

    async def can_handle(self, context: AgentContext) -> bool:
        """Check if this is a claims-related inquiry"""
        claims_keywords = [
            "claim", "denied", "denial", "eob", "explanation of benefits",
            "reimbursement", "paid", "processed", "submitted", "pending"
        ]

        text = f"{context.inquiry_title} {context.inquiry_description}".lower()
        return context.current_category == "claims" or any(kw in text for kw in claims_keywords)

    async def process(self, context: AgentContext) -> AgentResponse:
        """Process a claims inquiry"""

        # Check if we should escalate
        if self.should_escalate(context):
            return AgentResponse(
                action=AgentAction.ESCALATE,
                message="This claims inquiry requires human review due to complexity or history.",
                requires_human=True,
                confidence=0.9
            )

        # Analyze the inquiry type
        inquiry_type = self._classify_inquiry(context)

        # Handle based on type
        if inquiry_type == "status_check":
            return await self._handle_status_check(context)
        elif inquiry_type == "denial":
            return await self._handle_denial(context)
        elif inquiry_type == "eob":
            return await self._handle_eob(context)
        elif inquiry_type == "reimbursement":
            return await self._handle_reimbursement(context)
        else:
            return await self._handle_general_claims(context)

    def _classify_inquiry(self, context: AgentContext) -> str:
        """Classify the type of claims inquiry"""
        text = f"{context.inquiry_title} {context.inquiry_description}".lower()

        if any(w in text for w in ["status", "where is", "check on", "submitted"]):
            return "status_check"
        elif any(w in text for w in ["denied", "denial", "rejected", "not covered"]):
            return "denial"
        elif any(w in text for w in ["eob", "explanation", "breakdown", "statement"]):
            return "eob"
        elif any(w in text for w in ["reimburse", "refund", "pay back", "out of pocket"]):
            return "reimbursement"
        else:
            return "general"

    async def _handle_status_check(self, context: AgentContext) -> AgentResponse:
        """Handle claim status inquiries"""
        # In production, this would query the claims system
        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""Thank you for your inquiry about your claim status.

I've located your account and can help you with claim information. To provide specific claim details, I'll need:
1. The date of service
2. The provider name
3. Or the claim reference number if you have it

Once I have this information, I can tell you:
- Current claim status (pending, processed, paid, denied)
- Any required actions
- Expected resolution timeline

Is there a specific claim you'd like me to look up?""",
            data={"inquiry_type": "status_check", "member_id": context.member_id},
            confidence=0.85
        )

    async def _handle_denial(self, context: AgentContext) -> AgentResponse:
        """Handle claim denial inquiries"""

        # Check policy details for appeal eligibility
        policy = context.policy_details or {}

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""I understand you're concerned about a claim denial. Let me help you understand your options.

**Common Denial Reasons:**
1. Service requires prior authorization
2. Out-of-network provider
3. Service not covered under plan
4. Missing or incorrect information
5. Duplicate claim submission

**Your Options:**
- **Request Reconsideration:** If there was an error, we can review
- **File an Appeal:** You have 180 days from denial to appeal
- **Expedited Appeal:** Available for urgent medical situations

To proceed, I'll need the claim number or date of service. Would you like me to:
1. Explain the specific denial reason
2. Start an appeal process
3. Check if this service can be covered differently""",
            data={"inquiry_type": "denial", "can_appeal": True},
            confidence=0.8
        )

    async def _handle_eob(self, context: AgentContext) -> AgentResponse:
        """Handle EOB clarification requests"""

        policy = context.policy_details or {}
        deductible = policy.get("deductible", 0)
        deductible_met = policy.get("deductible_met", 0)

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""I can help explain your Explanation of Benefits (EOB).

**Your Current Coverage Status:**
- Deductible: ${deductible:,.2f} (${deductible_met:,.2f} met)
- Remaining Deductible: ${deductible - deductible_met:,.2f}

**Understanding Your EOB:**
- **Billed Amount:** What the provider charged
- **Allowed Amount:** What we've agreed to pay for this service
- **Paid Amount:** What we paid to the provider
- **Your Responsibility:** Copay, coinsurance, or deductible you owe

Would you like me to explain a specific EOB? Please provide the date of service or claim number.""",
            data={"inquiry_type": "eob"},
            confidence=0.85
        )

    async def _handle_reimbursement(self, context: AgentContext) -> AgentResponse:
        """Handle reimbursement inquiries"""
        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""I can help with your reimbursement question.

**Reimbursement Process:**
1. Submit itemized receipt with procedure codes
2. Include proof of payment
3. Processing typically takes 10-14 business days
4. Reimbursement sent via check or direct deposit

**Required Documentation:**
- Provider's itemized bill (with CPT codes)
- Proof of payment (receipt or credit card statement)
- Completed claim form (available on our portal)

**Important Notes:**
- Out-of-network services reimbursed at out-of-network rates
- Subject to deductible and coinsurance
- Submit within 365 days of service date

Would you like me to:
1. Check the status of a pending reimbursement
2. Help you submit a new reimbursement request
3. Calculate estimated reimbursement amount""",
            data={"inquiry_type": "reimbursement"},
            confidence=0.85
        )

    async def _handle_general_claims(self, context: AgentContext) -> AgentResponse:
        """Handle general claims inquiries"""
        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""I'm here to help with your claims question.

I can assist you with:
- **Claim Status:** Check where your claim is in processing
- **Claim Denials:** Understand why a claim was denied and your options
- **EOB Questions:** Explain your Explanation of Benefits
- **Reimbursement:** Help with out-of-pocket reimbursement requests

Please provide more details about your specific situation, and I'll guide you through the process.""",
            data={"inquiry_type": "general"},
            confidence=0.7
        )
