"""
Benefits Advisor Agent

Handles coverage questions, benefits explanations, cost estimates,
and provider network inquiries.
"""

from .base_agent import BaseAgent, AgentContext, AgentResponse, AgentAction
from typing import Dict, Any, List, Optional


class BenefitsAgent(BaseAgent):
    """
    Specialized agent for handling benefits and coverage inquiries.

    Capabilities:
    - Coverage verification
    - Cost estimation
    - In-network provider search
    - Plan comparison
    - Deductible/OOP tracking
    - Preventive care benefits
    """

    def __init__(self):
        super().__init__(
            name="benefits_agent",
            description="Handles coverage questions, benefits explanations, and cost estimates"
        )
        self.capabilities = [
            "coverage_check",
            "cost_estimation",
            "provider_search",
            "plan_comparison",
            "deductible_tracking",
            "preventive_care"
        ]

    async def can_handle(self, context: AgentContext) -> bool:
        """Check if this is a benefits-related inquiry"""
        benefits_keywords = [
            "covered", "coverage", "benefit", "cost", "pay", "copay",
            "deductible", "out of pocket", "in-network", "out-of-network",
            "provider", "doctor", "specialist", "preventive", "plan"
        ]

        text = f"{context.inquiry_title} {context.inquiry_description}".lower()
        return context.current_category == "coverage" or any(kw in text for kw in benefits_keywords)

    async def process(self, context: AgentContext) -> AgentResponse:
        """Process a benefits inquiry"""

        inquiry_type = self._classify_inquiry(context)

        if inquiry_type == "coverage_check":
            return await self._handle_coverage_check(context)
        elif inquiry_type == "cost_estimate":
            return await self._handle_cost_estimate(context)
        elif inquiry_type == "provider_search":
            return await self._handle_provider_search(context)
        elif inquiry_type == "deductible":
            return await self._handle_deductible_inquiry(context)
        elif inquiry_type == "preventive":
            return await self._handle_preventive_care(context)
        else:
            return await self._handle_general_benefits(context)

    def _classify_inquiry(self, context: AgentContext) -> str:
        """Classify the type of benefits inquiry"""
        text = f"{context.inquiry_title} {context.inquiry_description}".lower()

        if any(w in text for w in ["is it covered", "does my plan", "am i covered", "cover"]):
            return "coverage_check"
        elif any(w in text for w in ["how much", "cost", "pay", "estimate", "price"]):
            return "cost_estimate"
        elif any(w in text for w in ["find", "provider", "doctor", "network", "near me"]):
            return "provider_search"
        elif any(w in text for w in ["deductible", "out of pocket", "oop", "max"]):
            return "deductible"
        elif any(w in text for w in ["preventive", "wellness", "annual", "checkup", "screening"]):
            return "preventive"
        else:
            return "general"

    async def _handle_coverage_check(self, context: AgentContext) -> AgentResponse:
        """Handle coverage verification inquiries"""

        policy = context.policy_details or {}
        plan_type = policy.get("plan_type", "Unknown")

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""I can help verify your coverage.

**Your Plan:** {plan_type}

**Generally Covered Services:**
- Preventive care (annual exams, immunizations, screenings)
- Hospital services (inpatient and outpatient)
- Emergency services
- Mental health and substance abuse
- Prescription drugs
- Lab work and diagnostic imaging
- Maternity and newborn care

**May Require Prior Authorization:**
- Advanced imaging (MRI, CT, PET)
- Specialty medications
- Surgical procedures
- Durable medical equipment
- Physical/Occupational therapy (after initial visits)

**What specific service would you like me to check?**
Please provide the service name, procedure, or treatment you're asking about, and I'll give you specific coverage details.""",
            data={"inquiry_type": "coverage_check", "plan_type": plan_type},
            confidence=0.85
        )

    async def _handle_cost_estimate(self, context: AgentContext) -> AgentResponse:
        """Handle cost estimation inquiries"""

        policy = context.policy_details or {}
        deductible = policy.get("deductible", 0)
        deductible_met = policy.get("deductible_met", 0)
        oop_max = policy.get("out_of_pocket_max", 0)
        oop_met = policy.get("out_of_pocket_met", 0)
        copay_primary = policy.get("copay_primary", 30)
        copay_specialist = policy.get("copay_specialist", 50)

        remaining_deductible = deductible - deductible_met

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""I can help estimate your out-of-pocket costs.

**Your Current Status:**
- Deductible: ${deductible:,.2f} (${deductible_met:,.2f} met, ${remaining_deductible:,.2f} remaining)
- Out-of-Pocket Max: ${oop_max:,.2f} (${oop_met:,.2f} met)
- Primary Care Copay: ${copay_primary:.2f}
- Specialist Copay: ${copay_specialist:.2f}

**How Costs Are Calculated:**
1. **Before deductible is met:** You pay 100% of allowed amount (up to deductible)
2. **After deductible:** You pay copay or coinsurance (typically 20%)
3. **After OOP max:** Plan pays 100%

**To Estimate a Specific Service:**
Please tell me:
- What service/procedure you need
- If it's with in-network or out-of-network provider
- Approximate date of service

I can then calculate your estimated cost based on your plan benefits.""",
            data={
                "deductible_remaining": remaining_deductible,
                "oop_remaining": oop_max - oop_met
            },
            confidence=0.85
        )

    async def _handle_provider_search(self, context: AgentContext) -> AgentResponse:
        """Handle provider network inquiries"""

        policy = context.policy_details or {}
        plan_type = policy.get("plan_type", "PPO")

        network_info = ""
        if plan_type == "HMO":
            network_info = "Your HMO plan requires you to use in-network providers and get referrals for specialists."
        elif plan_type == "PPO":
            network_info = "Your PPO plan allows you to see any provider, but you'll save money with in-network providers."
        elif plan_type == "EPO":
            network_info = "Your EPO plan requires in-network providers except for emergencies."

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""I can help you find in-network providers.

**Your Plan Type:** {plan_type}
{network_info}

**How to Find In-Network Providers:**

1. **Online Provider Directory:**
   Visit healthfirst.com/find-a-doctor
   - Search by specialty, location, or name
   - Filter by accepting new patients
   - View ratings and reviews

2. **Mobile App:**
   Download the HealthFirst app
   - GPS-based provider search
   - Real-time availability
   - Direct appointment scheduling

3. **Call Member Services:**
   1-800-555-0100
   - We can search for you
   - Verify provider participation
   - Confirm accepting new patients

**What type of provider are you looking for?**
- Primary Care Physician
- Specialist (please specify)
- Urgent Care / Walk-in Clinic
- Hospital / Facility
- Mental Health Provider
- Other""",
            data={"plan_type": plan_type},
            confidence=0.85
        )

    async def _handle_deductible_inquiry(self, context: AgentContext) -> AgentResponse:
        """Handle deductible and out-of-pocket inquiries"""

        policy = context.policy_details or {}
        deductible = policy.get("deductible", 0)
        deductible_met = policy.get("deductible_met", 0)
        oop_max = policy.get("out_of_pocket_max", 0)
        oop_met = policy.get("out_of_pocket_met", 0)

        deductible_pct = (deductible_met / deductible * 100) if deductible > 0 else 0
        oop_pct = (oop_met / oop_max * 100) if oop_max > 0 else 0

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""Here's your deductible and out-of-pocket status.

**DEDUCTIBLE STATUS**
━━━━━━━━━━━━━━━━━━━━
Annual Deductible: ${deductible:,.2f}
Amount Met: ${deductible_met:,.2f}
Remaining: ${deductible - deductible_met:,.2f}
Progress: {deductible_pct:.0f}% {"✓ MET" if deductible_met >= deductible else ""}

**OUT-OF-POCKET MAXIMUM**
━━━━━━━━━━━━━━━━━━━━━━━━
Annual Maximum: ${oop_max:,.2f}
Amount Met: ${oop_met:,.2f}
Remaining: ${oop_max - oop_met:,.2f}
Progress: {oop_pct:.0f}% {"✓ MET" if oop_met >= oop_max else ""}

**What This Means:**
{"Your deductible is met! Most services now only require copay/coinsurance." if deductible_met >= deductible else "You're still working toward your deductible. You'll pay full allowed amounts until it's met."}

{"Congratulations! You've met your out-of-pocket max. Covered services are now paid at 100%." if oop_met >= oop_max else ""}

**Note:** Deductibles and OOP maximums reset on your plan anniversary date.

Would you like me to explain what counts toward your deductible?""",
            data={
                "deductible": deductible,
                "deductible_met": deductible_met,
                "oop_max": oop_max,
                "oop_met": oop_met
            },
            confidence=0.95
        )

    async def _handle_preventive_care(self, context: AgentContext) -> AgentResponse:
        """Handle preventive care inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Preventive Care Benefits**

Your plan covers these preventive services at **100% (no cost to you)** when using in-network providers:

**Annual Wellness:**
- Annual physical exam
- Well-woman exam
- Immunizations (flu, Tdap, etc.)

**Screenings by Age:**
- Colonoscopy (45+)
- Mammogram (40+)
- Prostate screening (50+)
- Bone density (65+)
- Diabetes screening (40+)
- Cholesterol screening (adults)
- Blood pressure screening

**Women's Health:**
- Contraception
- Prenatal care visits
- Breastfeeding support
- HPV testing

**Children's Preventive:**
- Well-child visits
- Developmental screenings
- Vision and hearing tests
- Immunization schedule

**Important Notes:**
- Must use in-network providers
- Diagnostic services (when symptoms present) may have cost share
- Frequency limits may apply

Would you like details about a specific preventive service?""",
            data={"inquiry_type": "preventive_care"},
            confidence=0.9
        )

    async def _handle_general_benefits(self, context: AgentContext) -> AgentResponse:
        """Handle general benefits inquiries"""

        policy = context.policy_details or {}
        plan_type = policy.get("plan_type", "Unknown")

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""I'm here to help with your benefits questions.

**Your Plan:** {plan_type}

**I can help you with:**

📋 **Coverage Verification**
   - Is a service/procedure covered?
   - What are the limitations?

💰 **Cost Estimates**
   - What will I pay out of pocket?
   - Deductible and coinsurance details

🏥 **Provider Network**
   - Find in-network providers
   - Check if your doctor is in-network

📊 **Deductible Tracking**
   - How much have I spent?
   - How much until I meet my deductible?

🩺 **Preventive Care**
   - What's covered at 100%?
   - Recommended screenings

📄 **Plan Documents**
   - Summary of Benefits
   - Evidence of Coverage

What would you like to know about your benefits?""",
            data={"plan_type": plan_type},
            confidence=0.8
        )
