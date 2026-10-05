"""
Member Services Agent

Handles general member service requests including ID cards,
account updates, PCP changes, and general inquiries.
"""

from .base_agent import BaseAgent, AgentContext, AgentResponse, AgentAction
from typing import Dict, Any, List


class MemberServicesAgent(BaseAgent):
    """
    Specialized agent for handling general member service requests.
    This is the default agent that handles miscellaneous inquiries.

    Capabilities:
    - ID card requests
    - Address/demographic updates
    - PCP changes
    - Plan documents
    - General questions
    - Portal/app support
    """

    def __init__(self):
        super().__init__(
            name="member_services_agent",
            description="Handles general member service requests and inquiries"
        )
        self.capabilities = [
            "id_card_request",
            "demographic_update",
            "pcp_change",
            "plan_documents",
            "portal_support",
            "general_inquiry"
        ]

    async def can_handle(self, context: AgentContext) -> bool:
        """Check if this is a member services inquiry"""
        member_keywords = [
            "id card", "card", "address", "phone", "email", "update",
            "change", "pcp", "primary care", "doctor", "document",
            "portal", "login", "password", "app", "account"
        ]

        text = f"{context.inquiry_title} {context.inquiry_description}".lower()
        return context.current_category == "member_services" or any(kw in text for kw in member_keywords)

    async def process(self, context: AgentContext) -> AgentResponse:
        """Process a member services inquiry"""

        inquiry_type = self._classify_inquiry(context)

        if inquiry_type == "id_card":
            return await self._handle_id_card(context)
        elif inquiry_type == "address_update":
            return await self._handle_address_update(context)
        elif inquiry_type == "pcp_change":
            return await self._handle_pcp_change(context)
        elif inquiry_type == "documents":
            return await self._handle_documents(context)
        elif inquiry_type == "portal":
            return await self._handle_portal_support(context)
        elif inquiry_type == "dependent":
            return await self._handle_dependent(context)
        else:
            return await self._handle_general_services(context)

    def _classify_inquiry(self, context: AgentContext) -> str:
        """Classify the type of member services inquiry"""
        text = f"{context.inquiry_title} {context.inquiry_description}".lower()

        if any(w in text for w in ["id card", "insurance card", "new card", "lost card", "replace card"]):
            return "id_card"
        elif any(w in text for w in ["address", "move", "phone", "email", "contact"]):
            return "address_update"
        elif any(w in text for w in ["pcp", "primary care", "change doctor", "new doctor"]):
            return "pcp_change"
        elif any(w in text for w in ["document", "summary", "benefits", "eoc", "handbook"]):
            return "documents"
        elif any(w in text for w in ["portal", "login", "password", "app", "website", "online"]):
            return "portal"
        elif any(w in text for w in ["dependent", "spouse", "child", "add", "remove"]):
            return "dependent"
        else:
            return "general"

    async def _handle_id_card(self, context: AgentContext) -> AgentResponse:
        """Handle ID card requests"""

        policy = context.policy_details or {}
        member_id = policy.get("member_id", context.member_id or "Unknown")

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""**ID Card Request**

I can help you get a new insurance ID card.

**Your Member ID:** {member_id}

**Digital ID Card (Instant)**
- Log in to member.healthfirst.com
- Click "ID Cards" in the menu
- View, download, or print instantly
- Also available in the HealthFirst mobile app

**Physical ID Card**
- Request online: member.healthfirst.com/id-card
- Call: 1-800-555-0100
- Processing: 7-10 business days
- Mailed to address on file

**Temporary Proof of Coverage**
While waiting for your new card:
- Use your digital ID card
- Providers can verify coverage by calling us
- Download temporary card from portal

**Information on Your ID Card:**
- Member name and ID
- Group number
- Plan type
- Effective date
- Copay amounts
- Customer service numbers

**Need Cards for Dependents?**
Specify which family members need cards when requesting.

Would you like me to process a card request now?""",
            data={"member_id": member_id, "action": "id_card_request"},
            confidence=0.9
        )

    async def _handle_address_update(self, context: AgentContext) -> AgentResponse:
        """Handle address and demographic updates"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Update Your Information**

Keep your contact information current to receive important communications.

**What You Can Update:**

📍 **Mailing Address**
- Where we send cards, EOBs, notices

📧 **Email Address**
- Digital communications preference

📱 **Phone Number**
- Primary and secondary contact

**How to Update:**

1. **Online (Fastest)**
   - Log in to member.healthfirst.com
   - Go to "My Profile" > "Personal Information"
   - Update and save changes
   - Changes effective immediately

2. **Mobile App**
   - Open HealthFirst app
   - Tap "Profile" > "Edit"
   - Update your information

3. **By Phone**
   - Call 1-800-555-0100
   - Verify your identity
   - Provide new information

**Important Notes:**
- Address changes may require proof of residency
- Notify us within 30 days of moving
- Some changes may affect your plan/network
- Moving out of state? Contact us about plan options

**What information would you like to update?**
- Address
- Phone number
- Email
- Other contact preferences""",
            data={"action": "demographic_update"},
            confidence=0.85
        )

    async def _handle_pcp_change(self, context: AgentContext) -> AgentResponse:
        """Handle PCP change requests"""

        policy = context.policy_details or {}
        plan_type = policy.get("plan_type", "Unknown")

        pcp_required = plan_type in ["HMO", "POS"]

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""**Primary Care Physician (PCP) Change**

Your Plan: **{plan_type}**
{"Your plan requires a PCP selection." if pcp_required else "Your plan allows you to see any in-network provider without a PCP."}

**How to Change Your PCP:**

1. **Online (Effective Immediately)**
   - Log in to member.healthfirst.com
   - Go to "My Doctor" or "PCP Selection"
   - Search for a new PCP
   - Select and confirm

2. **By Phone**
   - Call 1-800-555-0100
   - Effective date: Usually immediate or 1st of next month

**Finding a New PCP:**
- Use our provider directory: healthfirst.com/find-doctor
- Filter by:
  - Location/distance
  - Language
  - Gender
  - Accepting new patients
  - Hospital affiliations

**Before You Change:**
- Verify the new doctor is in-network
- Confirm they're accepting new patients
- Check their hospital affiliations
- Consider any ongoing treatment needs

**Specialist Referrals:**
{"Your HMO plan requires referrals from your PCP to see specialists." if plan_type == "HMO" else "Your plan may not require referrals for specialists."}

**Would you like help finding a new PCP?**
Tell me your:
- ZIP code or city
- Any preferences (gender, language, etc.)
- Any specific specialties needed""",
            data={"plan_type": plan_type, "pcp_required": pcp_required},
            confidence=0.85
        )

    async def _handle_documents(self, context: AgentContext) -> AgentResponse:
        """Handle plan document requests"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Plan Documents**

Access your important plan documents anytime.

**Available Documents:**

📋 **Summary of Benefits and Coverage (SBC)**
- Overview of your plan
- Covered services
- Cost sharing details
- Coverage examples

📖 **Evidence of Coverage (EOC)**
- Detailed plan handbook
- All covered benefits
- Exclusions and limitations
- Member rights and responsibilities

💳 **ID Cards**
- Digital and physical cards
- Print on demand

📊 **Explanation of Benefits (EOB)**
- Claim processing details
- What was paid
- Your responsibility

📄 **Tax Documents**
- 1095 forms for tax filing
- Premium statements

**How to Access:**

**Online Portal:**
1. Log in to member.healthfirst.com
2. Navigate to "Documents" or "Plan Information"
3. Download or print

**Mobile App:**
- Documents section for quick access

**Request by Mail:**
- Call 1-800-555-0100
- We'll mail documents within 5-7 business days

**Which document do you need?**
- Summary of Benefits (SBC)
- Evidence of Coverage (EOC)
- ID Card
- EOB statements
- Tax forms (1095)""",
            data={"action": "document_request"},
            confidence=0.85
        )

    async def _handle_portal_support(self, context: AgentContext) -> AgentResponse:
        """Handle portal and app support"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Member Portal & App Support**

I can help you with online account access.

**Common Issues:**

🔐 **Can't Log In**
- Visit: member.healthfirst.com
- Click "Forgot Password"
- Enter your email or member ID
- Check email for reset link

👤 **First Time Registration**
1. Go to member.healthfirst.com/register
2. Enter your Member ID (on your ID card)
3. Verify your identity
4. Create username and password
5. Set up security questions

📱 **Mobile App**
- Download "HealthFirst" from App Store or Google Play
- Use same login as web portal
- Enable biometric login for convenience

**Portal Features:**
- View ID cards
- Check claims status
- Find doctors
- Manage prescriptions
- Pay bills
- Update information
- Message your care team
- Access plan documents

**Technical Issues:**
- Clear browser cache and cookies
- Try a different browser
- Update the mobile app
- Disable VPN if using one

**Still Having Trouble?**
- Tech Support: 1-800-555-0101
- Available Mon-Fri 7am-9pm

What specific issue are you experiencing?""",
            data={"action": "portal_support"},
            confidence=0.85
        )

    async def _handle_dependent(self, context: AgentContext) -> AgentResponse:
        """Handle dependent-related inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Dependent Changes**

I can help you with adding or removing dependents.

**Adding a Dependent:**

📅 **Qualifying Life Events (QLE)**
- Marriage (add spouse)
- Birth or adoption (add child)
- Loss of other coverage
- Must notify within 30-60 days

**Required Documentation:**
- Marriage certificate (spouse)
- Birth certificate (newborn)
- Adoption papers
- Social Security number
- Proof of loss of coverage (if applicable)

**How to Add:**
1. Log in to member.healthfirst.com
2. Go to "Manage Dependents"
3. Select "Add Dependent"
4. Upload required documents
5. Or call 1-800-555-0100

**Removing a Dependent:**

Common reasons:
- Divorce
- Child ages out (26 for medical)
- Death
- Gains other coverage

**Dependent Coverage Rules:**
- Children covered until age 26
- Spouse covered until divorce finalized
- Domestic partners (where applicable)
- Disabled adult children may extend

**Cost Impact:**
- Adding dependents will increase your premium
- Removing dependents may decrease your premium
- Changes typically effective 1st of following month

**What change do you need to make?**
- Add spouse
- Add child (newborn, adoption, etc.)
- Remove dependent
- Update dependent information""",
            data={"action": "dependent_change"},
            confidence=0.85
        )

    async def _handle_general_services(self, context: AgentContext) -> AgentResponse:
        """Handle general member services inquiries"""

        policy = context.policy_details or {}
        member_name = f"{policy.get('first_name', '')} {policy.get('last_name', '')}".strip() or "Member"

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""**Member Services - How Can I Help?**

Hello{', ' + member_name if member_name != 'Member' else ''}! I'm here to assist with your account needs.

**Quick Services:**

💳 **ID Cards**
- Request new or replacement cards
- Access digital ID instantly

📝 **Update Information**
- Address, phone, email
- Communication preferences

👨‍⚕️ **Change Your PCP**
- Find a new primary care doctor
- Update your selection

👨‍👩‍👧 **Manage Dependents**
- Add or remove family members
- Update dependent information

📄 **Plan Documents**
- Summary of Benefits
- Evidence of Coverage
- Tax forms

💻 **Portal/App Help**
- Login assistance
- Registration help
- Technical support

📞 **Contact Us**
- Member Services: 1-800-555-0100
- 24/7 Nurse Line: 1-800-555-NURSE
- TTY: 1-800-555-0102

**Self-Service Options:**
- Web: member.healthfirst.com
- App: HealthFirst Mobile

What can I help you with today?""",
            data={"action": "general_services"},
            confidence=0.75
        )
