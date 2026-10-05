"""
Proactive Outreach Agent

Handles proactive member engagement including preventive care reminders,
wellness programs, care gaps, and health risk assessments.
"""

from .base_agent import BaseAgent, AgentContext, AgentResponse, AgentAction
from typing import Dict, Any, List, Optional
from datetime import datetime, date


class ProactiveOutreachAgent(BaseAgent):
    """
    Specialized agent for proactive member engagement and wellness.

    Capabilities:
    - Preventive care reminders
    - Care gap identification
    - Wellness program enrollment
    - Health risk assessments
    - Chronic condition management
    - Annual enrollment guidance
    """

    def __init__(self):
        super().__init__(
            name="proactive_outreach_agent",
            description="Handles proactive member engagement and wellness programs"
        )
        self.capabilities = [
            "preventive_care_reminders",
            "care_gap_closure",
            "wellness_programs",
            "health_assessments",
            "chronic_care_management",
            "enrollment_guidance"
        ]

    async def can_handle(self, context: AgentContext) -> bool:
        """Check if this is a proactive outreach inquiry"""
        outreach_keywords = [
            "wellness", "preventive", "screening", "reminder", "checkup",
            "annual", "health assessment", "program", "coaching", "fitness",
            "chronic", "management", "diabetes", "heart", "weight", "smoking"
        ]

        text = f"{context.inquiry_title} {context.inquiry_description}".lower()
        return context.current_category == "wellness" or any(kw in text for kw in outreach_keywords)

    async def process(self, context: AgentContext) -> AgentResponse:
        """Process a wellness/outreach inquiry"""

        inquiry_type = self._classify_inquiry(context)

        if inquiry_type == "preventive_care":
            return await self._handle_preventive_care(context)
        elif inquiry_type == "wellness_program":
            return await self._handle_wellness_program(context)
        elif inquiry_type == "chronic_care":
            return await self._handle_chronic_care(context)
        elif inquiry_type == "health_assessment":
            return await self._handle_health_assessment(context)
        elif inquiry_type == "care_gaps":
            return await self._handle_care_gaps(context)
        elif inquiry_type == "enrollment":
            return await self._handle_enrollment(context)
        else:
            return await self._handle_general_wellness(context)

    def _classify_inquiry(self, context: AgentContext) -> str:
        """Classify the type of wellness inquiry"""
        text = f"{context.inquiry_title} {context.inquiry_description}".lower()

        if any(w in text for w in ["preventive", "screening", "annual exam", "checkup", "mammogram", "colonoscopy"]):
            return "preventive_care"
        elif any(w in text for w in ["wellness program", "gym", "fitness", "weight loss", "smoking", "coaching"]):
            return "wellness_program"
        elif any(w in text for w in ["chronic", "diabetes", "heart", "asthma", "copd", "condition management"]):
            return "chronic_care"
        elif any(w in text for w in ["health assessment", "hra", "risk assessment", "health survey"]):
            return "health_assessment"
        elif any(w in text for w in ["care gap", "overdue", "missing", "need to schedule"]):
            return "care_gaps"
        elif any(w in text for w in ["enroll", "open enrollment", "change plan", "switch plan"]):
            return "enrollment"
        else:
            return "general"

    async def _handle_preventive_care(self, context: AgentContext) -> AgentResponse:
        """Handle preventive care inquiries and reminders"""

        policy = context.policy_details or {}
        member_age = self._calculate_age(policy.get("date_of_birth"))
        gender = policy.get("gender", "unknown")

        recommendations = self._get_preventive_recommendations(member_age, gender)

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""**Preventive Care - Stay Healthy!**

Preventive care is covered at **100%** with in-network providers - no copay, no deductible!

**Your Recommended Screenings:**
{recommendations}

**How to Schedule:**

1. **Find In-Network Providers:**
   - Visit healthfirst.com/find-doctor
   - Call 1-800-555-0100
   - Use the HealthFirst mobile app

2. **Schedule Your Appointment:**
   - Call the provider directly
   - Many offer online scheduling
   - Request "preventive/wellness visit"

**Important Tips:**
- Tell the scheduler this is a PREVENTIVE visit
- Confirm the provider is IN-NETWORK
- Bring your insurance card
- Share any concerns during your visit

**Preventive Care Benefits:**
✓ Annual physical exam
✓ Well-woman visits
✓ Immunizations
✓ Age-appropriate screenings
✓ Preventive counseling

**What's NOT Preventive:**
- Visits for specific symptoms or illness
- Follow-up appointments
- Diagnostic tests ordered due to symptoms
(These may have cost-sharing)

**Track Your Health:**
Log in to member.healthfirst.com to:
- View your preventive care checklist
- See which screenings you've completed
- Get personalized reminders

Would you like help scheduling any of these preventive services?""",
            data={
                "inquiry_type": "preventive_care",
                "member_age": member_age
            },
            confidence=0.9
        )

    def _calculate_age(self, dob: Optional[str]) -> int:
        """Calculate age from date of birth"""
        if not dob:
            return 40  # Default age for recommendations
        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
            today = date.today()
            return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        except (ValueError, TypeError):
            return 40

    def _get_preventive_recommendations(self, age: int, gender: str) -> str:
        """Get age/gender appropriate preventive care recommendations"""
        recommendations = []

        # Universal recommendations
        recommendations.append("✓ **Annual Physical Exam** - Once per year")
        recommendations.append("✓ **Blood Pressure Screening** - At each visit")
        recommendations.append("✓ **Cholesterol Screening** - Every 4-6 years (more often with risk factors)")
        recommendations.append("✓ **Flu Vaccine** - Annually")

        # Age-based recommendations
        if age >= 45:
            recommendations.append("✓ **Colorectal Cancer Screening** - Starting at 45, every 10 years (colonoscopy)")
            recommendations.append("✓ **Diabetes Screening** - Every 3 years")

        if age >= 50:
            recommendations.append("✓ **Shingles Vaccine** - Two doses")
            recommendations.append("✓ **Lung Cancer Screening** - Annual CT if smoking history")

        if age >= 65:
            recommendations.append("✓ **Pneumonia Vaccine** - As recommended")
            recommendations.append("✓ **Bone Density Screening** - As recommended")

        # Gender-based recommendations
        if gender.lower() in ["female", "f"]:
            recommendations.append("✓ **Well-Woman Exam** - Annually")
            if age >= 21:
                recommendations.append("✓ **Cervical Cancer Screening (Pap)** - Every 3 years")
            if age >= 40:
                recommendations.append("✓ **Mammogram** - Every 1-2 years")
            recommendations.append("✓ **Contraceptive Counseling** - As needed")

        if gender.lower() in ["male", "m"] and age >= 50:
            recommendations.append("✓ **Prostate Cancer Screening** - Discuss with your doctor")

        return "\n".join(recommendations)

    async def _handle_wellness_program(self, context: AgentContext) -> AgentResponse:
        """Handle wellness program inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Wellness Programs - Earn Rewards While Getting Healthy!**

HealthFirst offers comprehensive wellness programs at no additional cost.

**Available Programs:**

🏋️ **Fitness Reimbursement**
- Up to $300/year for gym membership
- Covers fitness apps and equipment
- Submit receipts for reimbursement
- [Enroll: member.healthfirst.com/fitness]

🍎 **Weight Management**
- Personalized nutrition coaching
- Weekly check-ins with health coach
- Meal planning resources
- Discounts on weight loss programs
- [Enroll: member.healthfirst.com/weight]

🚭 **Tobacco Cessation**
- Free nicotine replacement therapy
- Behavioral counseling
- Support groups
- Mobile app support
- Quit-line: 1-800-555-QUIT

🧘 **Stress Management**
- Mindfulness and meditation apps
- Virtual counseling sessions
- Stress reduction workshops
- Work-life balance resources

💤 **Sleep Wellness**
- Sleep assessment
- Sleep coaching
- Discounts on sleep aids
- Education materials

🏃 **Activity Challenges**
- Monthly step challenges
- Team competitions
- Prizes and rewards
- Sync your fitness tracker

**Wellness Rewards Program:**
Earn points for healthy activities:
| Activity | Points |
|----------|--------|
| Annual physical | 500 |
| Flu shot | 100 |
| Health assessment | 250 |
| Wellness program completion | 300 |
| Monthly activity goal | 50 |

**Redeem Points For:**
- Gift cards
- Premium credits
- Fitness equipment
- Charitable donations

**How to Enroll:**
1. Log in to member.healthfirst.com
2. Go to "Wellness Center"
3. Choose your programs
4. Start earning rewards!

Which program interests you most?""",
            data={"inquiry_type": "wellness_program"},
            confidence=0.9
        )

    async def _handle_chronic_care(self, context: AgentContext) -> AgentResponse:
        """Handle chronic condition management inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Chronic Condition Management Programs**

Living with a chronic condition? We're here to help you thrive.

**Disease Management Programs:**

💙 **Diabetes Care**
- Blood glucose monitoring supplies covered
- Diabetes educator consultations
- Nutrition counseling
- Eye and foot exam reminders
- A1C testing reminders
- Free glucometer program

❤️ **Heart Health**
- Cardiac rehabilitation coverage
- Blood pressure monitoring
- Cholesterol management
- Medication therapy management
- Lifestyle coaching

🫁 **Respiratory Care (Asthma/COPD)**
- Asthma action plan support
- Pulmonary rehabilitation
- Medication management
- Air quality alerts
- Inhaler technique coaching

🏥 **Complex Care Management**
- Dedicated care coordinator
- Care plan development
- Provider coordination
- Transition of care support
- 24/7 nurse line access

**Program Benefits:**
✓ **No extra cost** - Included with your plan
✓ **Personal health coach** - Regular check-ins
✓ **Educational resources** - Condition-specific materials
✓ **Medication support** - Adherence programs, lower costs
✓ **Care coordination** - Help navigating the system

**How to Enroll:**

1. **Self-Enroll Online:**
   - member.healthfirst.com/chronic-care
   - Select your condition(s)
   - Complete intake questionnaire

2. **Phone Enrollment:**
   - Call 1-800-555-CARE
   - Speak with a care coordinator
   - Available Mon-Fri 8am-8pm

3. **Provider Referral:**
   - Your doctor can refer you
   - We'll reach out to you

**What to Expect:**
1. Initial health assessment
2. Personalized care plan
3. Regular coach check-ins (phone/video)
4. Goal setting and tracking
5. Ongoing support and adjustments

**Special Benefits for Chronic Conditions:**
- Reduced copays on certain medications
- Extra preventive screenings covered
- Mail-order pharmacy savings
- Durable medical equipment coverage

Which condition would you like support with?""",
            data={"inquiry_type": "chronic_care"},
            confidence=0.9
        )

    async def _handle_health_assessment(self, context: AgentContext) -> AgentResponse:
        """Handle health risk assessment inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Health Risk Assessment (HRA)**

Complete your annual Health Risk Assessment to get personalized health insights!

**What is an HRA?**
A confidential questionnaire about your health, lifestyle, and family history that helps:
- Identify potential health risks
- Recommend preventive screenings
- Personalize your care
- Connect you with resources

**Benefits of Completing Your HRA:**

🎁 **Earn Wellness Rewards**
- 250 points toward rewards program
- Potential premium discount
- Gift card eligibility

📊 **Get Personalized Report**
- Health risk score
- Areas of strength
- Improvement opportunities
- Action recommendations

🏥 **Improve Your Care**
- Results shared with your doctor (with permission)
- Tailored health resources
- Program recommendations

**How to Complete:**

**Online (Recommended - 15 minutes):**
1. Log in to member.healthfirst.com
2. Go to "Health Assessment"
3. Answer questions honestly
4. Get instant results

**By Phone:**
- Call 1-800-555-HEALTH
- Complete with a health coach
- Great for questions or assistance

**On Paper:**
- Request mailed questionnaire
- Return in prepaid envelope
- Results mailed within 2 weeks

**What's Included:**

📋 **Health History**
- Medical conditions
- Medications
- Family history
- Surgeries

🍎 **Lifestyle Factors**
- Nutrition habits
- Physical activity
- Sleep quality
- Stress levels

😊 **Emotional Wellbeing**
- Mental health screening
- Social connections
- Work-life balance

🚨 **Risk Behaviors**
- Tobacco use
- Alcohol consumption
- Safety practices

**Privacy Assurance:**
- HIPAA protected
- Used only for your health improvement
- Never affects your coverage or rates
- You control who sees results

**After Your Assessment:**
- View detailed report online
- Receive personalized recommendations
- Get enrolled in relevant programs
- Set health goals

Would you like to start your Health Risk Assessment now?""",
            data={"inquiry_type": "health_assessment"},
            confidence=0.9
        )

    async def _handle_care_gaps(self, context: AgentContext) -> AgentResponse:
        """Handle care gap inquiries"""

        policy = context.policy_details or {}

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Care Gaps - Close the Gap, Improve Your Health**

Care gaps are preventive services or screenings that are recommended but not yet completed.

**Your Care Gap Dashboard:**
Log in to member.healthfirst.com/care-gaps to see:
- Overdue screenings
- Upcoming preventive care
- Completed services
- Personalized recommendations

**Common Care Gaps:**

📅 **Annual Wellness Visit**
- Recommended: Once per year
- Due: Check your account
- Schedule: Call your PCP or use online booking

💉 **Immunizations**
- Flu shot (annual)
- COVID-19 boosters
- Shingles, pneumonia (age-based)
- Tdap (every 10 years)

🔬 **Cancer Screenings**
- Mammogram (women 40+)
- Colonoscopy (adults 45+)
- Cervical cancer (women 21+)
- Prostate discussion (men 50+)

💊 **Chronic Condition Management**
- A1C test (diabetics)
- Eye exam (diabetics)
- Blood pressure check
- Medication adherence

**Why Close Care Gaps?**

✓ **Better Health Outcomes**
- Catch problems early
- Prevent serious conditions
- Manage existing conditions

✓ **Cost Savings**
- Preventive care is free
- Avoid expensive treatments later
- Lower out-of-pocket costs

✓ **Rewards**
- Earn wellness points
- Complete challenges
- Potential premium credits

**How We Help:**
- Reminder calls and emails
- Easy online scheduling
- Transportation assistance
- Interpreter services

**Barriers to Care?**
Tell us if you face:
- Transportation issues
- Work schedule conflicts
- Childcare needs
- Financial concerns
- Language barriers

We have resources to help!

**Ready to Close Your Care Gaps?**
Call your doctor or use member.healthfirst.com to schedule your preventive services today.

Would you like me to look up your specific care gaps?""",
            data={"inquiry_type": "care_gaps"},
            confidence=0.85
        )

    async def _handle_enrollment(self, context: AgentContext) -> AgentResponse:
        """Handle enrollment-related inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Enrollment & Plan Changes**

I can help you with enrollment questions and plan changes.

**Open Enrollment Period:**
📅 November 1 - December 15 (typically)
- Choose or change your plan for next year
- Compare plan options
- Changes effective January 1

**Special Enrollment Periods (SEP):**
You may enroll or change plans within 60 days of:
- Loss of other coverage
- Marriage or divorce
- Birth or adoption
- Moving to new area
- Change in income
- Other qualifying events

**How to Enroll/Change Plans:**

**Online (Recommended):**
1. Visit healthfirst.com/enroll
2. Compare plans side-by-side
3. Select your plan
4. Complete enrollment

**By Phone:**
- Call 1-800-555-ENROLL
- Mon-Fri 8am-8pm, Sat 9am-5pm
- Licensed agents available

**In Person:**
- Visit local enrollment center
- Find locations at healthfirst.com/locations

**When Comparing Plans, Consider:**
- Monthly premium
- Deductible amount
- Copays and coinsurance
- Out-of-pocket maximum
- Provider network
- Prescription coverage
- Extra benefits (dental, vision)

**Documents You'll Need:**
- Social Security numbers (all enrollees)
- Date of birth for each person
- Current address
- Income information (for marketplace plans)
- Current insurance information

**After Enrolling:**
1. Receive confirmation within 5-7 days
2. ID cards mailed before effective date
3. Set up online account
4. Choose a PCP (if HMO)

**Questions About Your Current Plan?**
- View benefits: member.healthfirst.com
- Call: 1-800-555-0100

What enrollment question can I help with?""",
            data={"inquiry_type": "enrollment"},
            confidence=0.85
        )

    async def _handle_general_wellness(self, context: AgentContext) -> AgentResponse:
        """Handle general wellness inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Wellness & Health Improvement**

Welcome to HealthFirst Wellness! We're here to help you live your healthiest life.

**Explore Our Wellness Resources:**

🏥 **Preventive Care**
- Annual exams and screenings
- Immunizations
- All covered at 100% in-network

💪 **Wellness Programs**
- Fitness reimbursement ($300/year)
- Weight management
- Tobacco cessation
- Stress management

❤️ **Chronic Care Management**
- Diabetes support
- Heart health
- Respiratory care
- Dedicated care coordinators

📊 **Health Assessment**
- Free annual health risk assessment
- Personalized health report
- Earn wellness rewards

📱 **Digital Health Tools**
- HealthFirst mobile app
- Fitness tracking integration
- Telehealth services
- Medication reminders

🏆 **Wellness Rewards**
- Earn points for healthy activities
- Redeem for gift cards and more
- Monthly challenges

**Quick Links:**
- Wellness Center: member.healthfirst.com/wellness
- Find a Doctor: healthfirst.com/find-doctor
- 24/7 Nurse Line: 1-800-555-NURSE

**Helpful Numbers:**
- Member Services: 1-800-555-0100
- Wellness Programs: 1-800-555-WELL
- Care Management: 1-800-555-CARE

**Not Sure Where to Start?**
Complete your Health Risk Assessment to get personalized recommendations!

What aspect of wellness would you like to explore?
1. Preventive care reminders
2. Wellness programs
3. Chronic condition support
4. Health assessment
5. Care gap review""",
            data={"inquiry_type": "general"},
            confidence=0.8
        )
