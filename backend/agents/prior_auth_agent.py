"""
Prior Authorization Agent

Handles prior authorization requests, status checks,
and expedited authorization for urgent medical needs.
"""

from .base_agent import BaseAgent, AgentContext, AgentResponse, AgentAction
from typing import Dict, Any, List


# Services that typically require prior authorization
PRIOR_AUTH_SERVICES = [
    "mri", "ct scan", "pet scan", "surgery", "hospitalization",
    "physical therapy", "occupational therapy", "speech therapy",
    "durable medical equipment", "dme", "home health", "skilled nursing",
    "infusion therapy", "specialty drugs", "genetic testing",
    "transplant", "bariatric surgery", "cosmetic", "experimental"
]


class PriorAuthAgent(BaseAgent):
    """
    Specialized agent for handling prior authorization inquiries.

    Capabilities:
    - Check if service requires prior auth
    - Submit prior auth requests
    - Track authorization status
    - Handle expedited/urgent requests
    - Explain denial and appeal process
    """

    def __init__(self):
        super().__init__(
            name="prior_auth_agent",
            description="Handles prior authorization requests and status inquiries"
        )
        self.capabilities = [
            "prior_auth_check",
            "auth_submission",
            "status_tracking",
            "expedited_processing",
            "auth_denial_appeals"
        ]

    async def can_handle(self, context: AgentContext) -> bool:
        """Check if this is a prior authorization inquiry"""
        auth_keywords = [
            "prior auth", "authorization", "pre-approval", "pre-auth",
            "approved", "approval", "authorize", "precertification"
        ]

        text = f"{context.inquiry_title} {context.inquiry_description}".lower()
        return context.current_category == "prior_authorization" or any(kw in text for kw in auth_keywords)

    async def process(self, context: AgentContext) -> AgentResponse:
        """Process a prior authorization inquiry"""

        # Check compliance requirements
        compliance_issues = await self.validate_compliance(context)

        # Classify the inquiry
        inquiry_type = self._classify_inquiry(context)

        # Check for urgent/expedited needs
        is_urgent = self._check_urgency(context)

        if inquiry_type == "check_requirement":
            return await self._check_auth_requirement(context)
        elif inquiry_type == "status":
            return await self._check_auth_status(context, is_urgent)
        elif inquiry_type == "submit":
            return await self._submit_auth_request(context, is_urgent)
        elif inquiry_type == "denial":
            return await self._handle_auth_denial(context)
        else:
            return await self._handle_general_auth(context)

    def _classify_inquiry(self, context: AgentContext) -> str:
        """Classify the type of prior auth inquiry"""
        text = f"{context.inquiry_title} {context.inquiry_description}".lower()

        if any(w in text for w in ["need", "require", "do i need", "does it need"]):
            return "check_requirement"
        elif any(w in text for w in ["status", "where", "check on", "pending", "submitted"]):
            return "status"
        elif any(w in text for w in ["submit", "request", "get", "need approval"]):
            return "submit"
        elif any(w in text for w in ["denied", "denial", "rejected", "appeal"]):
            return "denial"
        else:
            return "general"

    def _check_urgency(self, context: AgentContext) -> bool:
        """Check if this is an urgent/expedited request"""
        urgent_keywords = [
            "urgent", "emergency", "asap", "immediately", "critical",
            "life-threatening", "expedited", "rush", "can't wait"
        ]
        text = f"{context.inquiry_title} {context.inquiry_description}".lower()
        return context.priority == "urgent" or any(kw in text for kw in urgent_keywords)

    def _detect_service(self, context: AgentContext) -> str:
        """Detect what service the member is asking about"""
        text = f"{context.inquiry_title} {context.inquiry_description}".lower()

        for service in PRIOR_AUTH_SERVICES:
            if service in text:
                return service

        return "unspecified"

    async def _check_auth_requirement(self, context: AgentContext) -> AgentResponse:
        """Check if a service requires prior authorization"""

        service = self._detect_service(context)
        policy = context.policy_details or {}
        requires_auth = policy.get("prior_auth_required", True)

        if service != "unspecified":
            return AgentResponse(
                action=AgentAction.RESPOND,
                message=f"""**Prior Authorization Check: {service.upper()}**

Based on your plan, here's what I found:

**Service:** {service.title()}
**Prior Auth Required:** {"Yes" if requires_auth else "No"}

{"This service typically requires prior authorization. I recommend getting approval before scheduling to ensure coverage." if requires_auth else "This service may not require prior authorization, but I recommend confirming with your provider."}

**Next Steps:**
1. Have your doctor submit the authorization request
2. Include clinical documentation supporting medical necessity
3. Standard processing: 5-7 business days
4. Expedited (if urgent): 24-72 hours

Would you like me to:
- Explain the authorization process
- Check if you have any pending authorizations
- Help with an expedited request""",
                data={"service": service, "requires_auth": requires_auth},
                confidence=0.85
            )
        else:
            return AgentResponse(
                action=AgentAction.REQUEST_INFO,
                message="""I can help you determine if prior authorization is needed.

**Please specify the service or procedure you're asking about:**
- Medical procedure or surgery
- Diagnostic imaging (MRI, CT, PET scan)
- Therapy services (PT, OT, speech)
- Durable medical equipment
- Specialty medications
- Other services

Once you provide the specific service, I can tell you:
- If prior authorization is required
- Documentation needed
- Processing timeline
- How to submit the request""",
                confidence=0.7
            )

    async def _check_auth_status(self, context: AgentContext, is_urgent: bool) -> AgentResponse:
        """Check the status of a prior authorization"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""I can check the status of your prior authorization.

**To look up your authorization, I need:**
1. Authorization reference number, OR
2. Date the request was submitted, OR
3. Service/procedure requested

**Current Processing Times:**
- Standard requests: 5-7 business days
- {"⚡ EXPEDITED (marked urgent): 24-72 hours" if is_urgent else "Expedited (if medically urgent): 24-72 hours"}

**Common Status Updates:**
- **Pending Review:** Waiting for clinical review
- **Additional Info Needed:** Provider must submit more documentation
- **Approved:** Authorization granted (check dates)
- **Denied:** Review denial letter for appeal options

Please provide your authorization details and I'll check the status immediately.""",
            data={"is_urgent": is_urgent},
            confidence=0.8
        )

    async def _submit_auth_request(self, context: AgentContext, is_urgent: bool) -> AgentResponse:
        """Guide through submitting a prior authorization request"""

        expedited_note = """
**⚡ EXPEDITED PROCESSING**
Since this appears urgent, I can flag this for expedited review (24-72 hours).
Expedited requests require documentation showing why standard timeframe
could seriously jeopardize life, health, or ability to regain maximum function.
""" if is_urgent else ""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""I can help you understand how to submit a prior authorization.

{expedited_note}

**Who Can Submit:**
Prior authorization requests must be submitted by your healthcare provider, not members directly.

**Required Information:**
1. Member ID and demographics
2. Provider NPI and contact info
3. Diagnosis codes (ICD-10)
4. Procedure codes (CPT/HCPCS)
5. Clinical documentation supporting medical necessity
6. Requested duration/quantity

**Submission Methods for Providers:**
- Online portal (fastest): provider.healthfirst.com
- Fax: 1-800-555-AUTH
- Phone: 1-800-555-0100

**What You Can Do:**
1. Confirm your provider has submitted the request
2. Provide me with details to check status
3. Follow up if no response within expected timeframe

Would you like me to explain the expedited process or check for existing requests?""",
            data={"is_urgent": is_urgent, "action": "submit_guidance"},
            confidence=0.85
        )

    async def _handle_auth_denial(self, context: AgentContext) -> AgentResponse:
        """Handle prior authorization denial inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""I understand your prior authorization was denied. Let me help you understand your options.

**Common Denial Reasons:**
- Service not medically necessary based on submitted documentation
- Alternative treatments should be tried first (step therapy)
- Out-of-network provider without OON authorization
- Incomplete or missing clinical information

**Your Appeal Rights:**
1. **Request Reconsideration:** Ask for review with additional documentation
2. **First Level Appeal:** Formal appeal within 180 days of denial
3. **Expedited Appeal:** For urgent medical situations (24-72 hour decision)
4. **External Review:** Independent review by third party

**To Start an Appeal:**
- Review the denial letter for specific reason
- Gather supporting clinical documentation
- Have your provider submit a letter of medical necessity
- Submit within appeal deadline

Would you like me to:
1. Explain the specific denial reason
2. Guide you through the appeal process
3. Check expedited appeal eligibility
4. Connect you with our appeals department""",
            data={"action": "denial_help"},
            requires_human=False,
            confidence=0.85
        )

    async def _handle_general_auth(self, context: AgentContext) -> AgentResponse:
        """Handle general prior authorization inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""I'm here to help with your prior authorization questions.

**What is Prior Authorization?**
Prior authorization is approval from us before you receive certain services,
to ensure they're medically necessary and covered under your plan.

**I can help you with:**
- Check if a service requires prior auth
- Understand the submission process
- Check status of pending authorizations
- Explain denial reasons and appeal options
- Process expedited requests for urgent needs

**Quick Links:**
- Service requiring auth list: healthfirst.com/prior-auth
- Provider portal: provider.healthfirst.com
- Member portal: member.healthfirst.com

What would you like help with today?""",
            confidence=0.75
        )
