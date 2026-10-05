"""
Appeals & Grievances Agent

Handles appeals for denied claims, grievances about service quality,
and escalation management with compliance tracking.
"""

from .base_agent import BaseAgent, AgentContext, AgentResponse, AgentAction
from typing import Dict, Any, List
from datetime import datetime, timedelta


class AppealsGrievancesAgent(BaseAgent):
    """
    Specialized agent for handling appeals and grievances.

    This agent ALWAYS requires human review due to regulatory requirements.

    Capabilities:
    - Appeal intake and tracking
    - Grievance documentation
    - Expedited appeal handling
    - External review guidance
    - Compliance timeline tracking
    """

    def __init__(self):
        super().__init__(
            name="appeals_grievances_agent",
            description="Handles appeals for denied claims and member grievances"
        )
        self.capabilities = [
            "appeal_intake",
            "grievance_filing",
            "expedited_appeal",
            "external_review",
            "timeline_tracking"
        ]
        # Regulatory timelines (in days)
        self.timelines = {
            "standard_appeal": 30,
            "expedited_appeal": 72,  # hours, not days
            "grievance": 30,
            "external_review": 45
        }

    async def can_handle(self, context: AgentContext) -> bool:
        """Check if this is an appeals or grievances inquiry"""
        appeals_keywords = [
            "appeal", "grievance", "complaint", "denied", "unfair",
            "reconsider", "review decision", "dispute decision", "overturn",
            "disagree", "not satisfied", "escalate", "supervisor"
        ]

        text = f"{context.inquiry_title} {context.inquiry_description}".lower()
        return context.current_category == "appeals_grievances" or any(kw in text for kw in appeals_keywords)

    async def process(self, context: AgentContext) -> AgentResponse:
        """Process an appeals or grievances inquiry"""

        inquiry_type = self._classify_inquiry(context)

        if inquiry_type == "appeal":
            return await self._handle_appeal(context)
        elif inquiry_type == "expedited_appeal":
            return await self._handle_expedited_appeal(context)
        elif inquiry_type == "grievance":
            return await self._handle_grievance(context)
        elif inquiry_type == "external_review":
            return await self._handle_external_review(context)
        elif inquiry_type == "status":
            return await self._handle_status_check(context)
        else:
            return await self._handle_general_appeals(context)

    def _classify_inquiry(self, context: AgentContext) -> str:
        """Classify the type of appeals/grievance inquiry"""
        text = f"{context.inquiry_title} {context.inquiry_description}".lower()

        if any(w in text for w in ["urgent", "emergency", "immediate", "life threatening", "expedited"]):
            return "expedited_appeal"
        elif any(w in text for w in ["external review", "independent", "outside review"]):
            return "external_review"
        elif any(w in text for w in ["appeal", "denied claim", "reconsider", "overturn"]):
            return "appeal"
        elif any(w in text for w in ["grievance", "complaint", "service", "treatment", "quality"]):
            return "grievance"
        elif any(w in text for w in ["status", "where is", "update on", "check on"]):
            return "status"
        else:
            return "general"

    async def _handle_appeal(self, context: AgentContext) -> AgentResponse:
        """Handle standard appeal requests"""

        deadline = datetime.now() + timedelta(days=180)

        return AgentResponse(
            action=AgentAction.ESCALATE,
            message=f"""**Appeal Request - Human Review Required**

I understand you want to appeal a coverage decision. Appeals are important rights that we take seriously.

**Your Appeal Rights:**
- You have **180 days** from the denial date to file an appeal
- Appeal deadline for this inquiry: **{deadline.strftime('%B %d, %Y')}**
- You or your authorized representative may file

**Types of Appeals:**

📋 **Standard Appeal (Level 1)**
- Internal review by different reviewer
- Decision within 30 days
- Written determination provided

⚡ **Expedited Appeal**
- For urgent medical situations
- Decision within 72 hours
- Available when standard timeframe could jeopardize health

🔍 **External Review (Level 2)**
- Independent third-party review
- Available after internal appeal exhausted
- Binding decision

**To File Your Appeal:**

**Required Information:**
1. Member ID and contact information
2. Claim number or denial letter reference
3. Date of service
4. Provider information
5. Reason you believe decision should be overturned
6. Supporting documentation (medical records, doctor's letter)

**Submission Methods:**
- **Online:** member.healthfirst.com/appeals
- **Mail:** Appeals Department, PO Box 54321, City, ST 12345
- **Fax:** 1-800-555-0150
- **Phone:** 1-800-555-0100 (to start the process)

**What Happens Next:**
1. We acknowledge receipt within 5 business days
2. Medical director reviews your case
3. We may request additional information
4. Written decision mailed within 30 days
5. If denied, you can request external review

**This case has been flagged for human review.**
A member services specialist will contact you within 1 business day to assist with your appeal.

Is this appeal related to an urgent medical situation?""",
            data={
                "inquiry_type": "appeal",
                "deadline": deadline.isoformat(),
                "timeline_days": 30
            },
            requires_human=True,
            confidence=0.85
        )

    async def _handle_expedited_appeal(self, context: AgentContext) -> AgentResponse:
        """Handle expedited/urgent appeal requests"""

        return AgentResponse(
            action=AgentAction.ESCALATE,
            message="""**EXPEDITED APPEAL REQUEST - URGENT REVIEW**

⚠️ **This is being treated as an urgent request**

Expedited appeals are available when waiting for a standard appeal could:
- Seriously jeopardize your life or health
- Jeopardize your ability to regain maximum function
- Cause severe pain that cannot be managed without the requested care

**Expedited Appeal Timeline:**
- Decision within **72 HOURS** (not 30 days)
- Verbal notification followed by written decision
- Available 24/7 for truly urgent situations

**To Qualify for Expedited Review:**
- Physician statement supporting urgency (we can contact your doctor directly)
- Documentation of medical necessity
- Explanation of harm from standard timeframe

**Immediate Steps We're Taking:**
1. ✓ Flagging this for immediate human review
2. ✓ Notifying our expedited appeals team
3. ✓ Preparing to contact your physician if needed

**What We Need From You:**
- Claim or denial reference number
- Treating physician's name and phone number
- Brief description of the urgent medical situation
- Best phone number to reach you

**Emergency Contact:**
📞 **Expedited Appeals Hotline: 1-800-555-0111**
Available 24 hours a day, 7 days a week

**IMPORTANT:**
If this is a medical emergency, please call 911 or go to the nearest emergency room. Emergency services are always covered regardless of authorization status.

**A specialist will contact you within 2 hours to process your expedited appeal.**

Please confirm: Is there an immediate health risk if this service is delayed?""",
            data={
                "inquiry_type": "expedited_appeal",
                "timeline_hours": 72,
                "priority": "urgent"
            },
            requires_human=True,
            confidence=0.95
        )

    async def _handle_grievance(self, context: AgentContext) -> AgentResponse:
        """Handle grievance/complaint filings"""

        return AgentResponse(
            action=AgentAction.ESCALATE,
            message="""**Grievance Filing - Member Complaint**

I understand you have a concern about the quality of care or service you received. We take all grievances seriously.

**What is a Grievance?**
A formal complaint about:
- Quality of care received
- Access to care issues
- Customer service concerns
- Waiting times
- Provider behavior
- Facility conditions
- Communication issues

**This is Different From an Appeal:**
- **Appeal:** Dispute a coverage decision
- **Grievance:** Complain about service or quality

**Grievance Process:**

📝 **Filing Your Grievance:**
- **Online:** member.healthfirst.com/grievance
- **Phone:** 1-800-555-0100
- **Mail:** Grievance Department, PO Box 54322
- **In Person:** Any member services location

📅 **Timeline:**
- Acknowledgment: Within 5 business days
- Investigation: We review within 30 days
- Written response: Mailed after investigation
- Extension: Up to 14 additional days if needed (we'll notify you)

**Information to Include:**
1. Your contact information
2. Date(s) of incident
3. Provider/facility name
4. Detailed description of concern
5. Names of staff involved (if known)
6. What resolution you're seeking
7. Any supporting documentation

**Your Rights:**
- No retaliation for filing a grievance
- Continued access to care during review
- Written response to your concern
- Escalation options if unsatisfied

**Quality Improvement:**
Your feedback helps us improve. All grievances are:
- Reviewed by our quality team
- Used to identify patterns
- Part of our accreditation process

**This has been escalated for human review.**
A member advocate will contact you within 2 business days.

Would you like to describe your concern in more detail?""",
            data={
                "inquiry_type": "grievance",
                "timeline_days": 30
            },
            requires_human=True,
            confidence=0.85
        )

    async def _handle_external_review(self, context: AgentContext) -> AgentResponse:
        """Handle external review requests"""

        return AgentResponse(
            action=AgentAction.ESCALATE,
            message="""**External Review Request**

You have the right to an independent, external review of our internal appeal decision.

**What is External Review?**
- Review by an independent third party (not HealthFirst)
- Conducted by state-certified reviewers
- Their decision is binding on us
- No cost to you

**Eligibility Requirements:**
✓ You must have completed our internal appeal process
✓ Request within 4 months of final internal decision
✓ Case involves medical judgment or rescission of coverage

**Types of External Review:**

🏥 **Standard External Review**
- For non-urgent coverage decisions
- Decision within 45 days
- Written determination provided

⚡ **Expedited External Review**
- For urgent situations
- Decision within 72 hours
- Available when delay could cause harm

**How to Request:**

1. **Complete Request Form:**
   - Available at member.healthfirst.com/external-review
   - Or call 1-800-555-0100 to request by mail

2. **Submit To:**
   - We forward to the Independent Review Organization (IRO)
   - Or submit directly to your state insurance department

3. **Include:**
   - Copy of internal appeal denial
   - Any additional medical information
   - Physician's statement (if available)

**External Review Organizations:**
Your case will be assigned to a state-certified IRO with appropriate medical expertise.

**Your State Insurance Department:**
[State] Department of Insurance
Consumer Assistance: [Phone]
Website: [URL]

**Important Notes:**
- External review is the final step in the appeals process
- The IRO decision is binding on HealthFirst
- You may still have legal options beyond external review

**This request requires human processing.**
A specialist will verify your eligibility and guide you through the process within 1 business day.

Do you have your internal appeal denial letter reference number?""",
            data={
                "inquiry_type": "external_review",
                "timeline_days": 45
            },
            requires_human=True,
            confidence=0.9
        )

    async def _handle_status_check(self, context: AgentContext) -> AgentResponse:
        """Handle appeal/grievance status inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Appeal/Grievance Status Check**

I can help you check the status of your appeal or grievance.

**Check Status Online:**
1. Log in to member.healthfirst.com
2. Go to "Appeals & Grievances"
3. View all submitted cases and their status

**Status Definitions:**

📥 **Received**
- We have your submission
- Review not yet started

📋 **Under Review**
- Being evaluated by our team
- May request additional information

👨‍⚕️ **Medical Director Review**
- For appeals: physician reviewing medical necessity
- Decision pending

📤 **Decision Made**
- Review complete
- Written determination being prepared

✉️ **Response Sent**
- Final decision mailed/sent
- Check mail or secure messages

**Typical Timelines:**

| Type | Standard Timeline |
|------|------------------|
| Standard Appeal | 30 days |
| Expedited Appeal | 72 hours |
| Grievance | 30 days |
| External Review | 45 days |

**Need Status Now?**
Call us at 1-800-555-0100 with your:
- Reference number (from acknowledgment letter)
- Or date you submitted
- Type of request (appeal or grievance)

**Haven't Received a Response?**
If your timeline has passed and you haven't heard from us:
- Call immediately
- We may need additional information
- Processing extension may apply

What is your appeal or grievance reference number?""",
            data={"inquiry_type": "status"},
            confidence=0.85
        )

    async def _handle_general_appeals(self, context: AgentContext) -> AgentResponse:
        """Handle general appeals/grievances inquiries"""

        return AgentResponse(
            action=AgentAction.ESCALATE,
            message="""**Appeals & Grievances - How Can We Help?**

I'm here to assist with appeals and grievances. Let me explain your options.

**Appeals** (Dispute a Coverage Decision)
Use when you disagree with:
- Claim denial
- Prior authorization denial
- Coverage determination
- Service reduction or termination

**Grievances** (File a Complaint)
Use when you're concerned about:
- Quality of care
- Customer service
- Access to care
- Provider/staff conduct

**Your Member Rights:**

✓ **Right to Appeal**
- File within 180 days of decision
- Multiple levels of review available
- Expedited options for urgent situations

✓ **Right to File Grievances**
- Formal process for complaints
- No retaliation
- Written response required

✓ **Right to Representation**
- Designate someone to act on your behalf
- Legal representation allowed
- Provider can appeal for you

**Quick Reference:**

| I want to... | File a... |
|--------------|-----------|
| Challenge a denied claim | Appeal |
| Dispute a decision | Appeal |
| Complain about service | Grievance |
| Report quality concerns | Grievance |
| Get a quicker decision | Expedited Appeal |
| Get an outside opinion | External Review |

**Contact Us:**
📞 Phone: 1-800-555-0100
📠 Fax: 1-800-555-0150
🌐 Online: member.healthfirst.com/appeals

**This inquiry has been flagged for human review** to ensure you receive proper guidance.

What would you like help with?
1. File an appeal
2. File a grievance
3. Check status of existing case
4. Understand a decision
5. Request expedited review""",
            data={"inquiry_type": "general"},
            requires_human=True,
            confidence=0.75
        )
