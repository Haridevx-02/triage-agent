"""
Billing Resolution Agent

Handles billing inquiries, payment issues, billing disputes,
payment plans, and refund processing.
"""

from .base_agent import BaseAgent, AgentContext, AgentResponse, AgentAction
from typing import Dict, Any, List


class BillingAgent(BaseAgent):
    """
    Specialized agent for handling billing and payment inquiries.

    Capabilities:
    - Bill explanation
    - Payment processing
    - Payment plan setup
    - Billing disputes
    - Refund requests
    - Balance billing resolution
    """

    def __init__(self):
        super().__init__(
            name="billing_agent",
            description="Handles billing inquiries, payments, disputes, and refunds"
        )
        self.capabilities = [
            "bill_explanation",
            "payment_processing",
            "payment_plan",
            "billing_dispute",
            "refund_request",
            "balance_billing"
        ]

    async def can_handle(self, context: AgentContext) -> bool:
        """Check if this is a billing-related inquiry"""
        billing_keywords = [
            "bill", "billing", "payment", "pay", "owe", "charge",
            "invoice", "statement", "premium", "refund", "dispute",
            "balance", "collection", "installment"
        ]

        text = f"{context.inquiry_title} {context.inquiry_description}".lower()
        return context.current_category == "billing" or any(kw in text for kw in billing_keywords)

    async def process(self, context: AgentContext) -> AgentResponse:
        """Process a billing inquiry"""

        inquiry_type = self._classify_inquiry(context)

        if inquiry_type == "bill_explanation":
            return await self._handle_bill_explanation(context)
        elif inquiry_type == "payment":
            return await self._handle_payment(context)
        elif inquiry_type == "payment_plan":
            return await self._handle_payment_plan(context)
        elif inquiry_type == "dispute":
            return await self._handle_dispute(context)
        elif inquiry_type == "refund":
            return await self._handle_refund(context)
        elif inquiry_type == "premium":
            return await self._handle_premium(context)
        elif inquiry_type == "balance_billing":
            return await self._handle_balance_billing(context)
        else:
            return await self._handle_general_billing(context)

    def _classify_inquiry(self, context: AgentContext) -> str:
        """Classify the type of billing inquiry"""
        text = f"{context.inquiry_title} {context.inquiry_description}".lower()

        if any(w in text for w in ["explain", "understand", "what is", "breakdown"]):
            return "bill_explanation"
        elif any(w in text for w in ["make payment", "pay my", "how to pay"]):
            return "payment"
        elif any(w in text for w in ["payment plan", "installment", "monthly", "can't afford"]):
            return "payment_plan"
        elif any(w in text for w in ["dispute", "incorrect", "wrong", "error", "shouldn't"]):
            return "dispute"
        elif any(w in text for w in ["refund", "overpaid", "reimbursement", "money back"]):
            return "refund"
        elif any(w in text for w in ["premium", "monthly payment", "insurance payment"]):
            return "premium"
        elif any(w in text for w in ["balance bill", "provider bill", "extra charge"]):
            return "balance_billing"
        else:
            return "general"

    async def _handle_bill_explanation(self, context: AgentContext) -> AgentResponse:
        """Handle bill explanation requests"""

        policy = context.policy_details or {}
        deductible = policy.get("deductible", 0)
        deductible_met = policy.get("deductible_met", 0)

        return AgentResponse(
            action=AgentAction.RESPOND,
            message=f"""I can help explain your bill.

**Understanding Your Bill:**

Your bill typically includes these components:

| Component | Description |
|-----------|-------------|
| **Billed Amount** | What the provider charged |
| **Allowed Amount** | Negotiated rate we pay |
| **Plan Paid** | What insurance covered |
| **Your Responsibility** | What you owe |

**Your Current Deductible Status:**
- Annual Deductible: ${deductible:,.2f}
- Amount Met: ${deductible_met:,.2f}
- Remaining: ${deductible - deductible_met:,.2f}

**Why You May Owe:**
1. **Deductible not met** - You pay until reaching ${deductible:,.2f}
2. **Coinsurance** - Your share (typically 20%) after deductible
3. **Copayment** - Fixed amount for certain services
4. **Non-covered services** - Services not in your plan
5. **Out-of-network** - Higher costs for OON providers

**To explain a specific bill, I need:**
- Date of service
- Provider name
- Claim or invoice number

Would you like me to look up a specific bill?""",
            data={"inquiry_type": "bill_explanation"},
            confidence=0.85
        )

    async def _handle_payment(self, context: AgentContext) -> AgentResponse:
        """Handle payment inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Payment Options**

You can pay your bill through several convenient methods:

**Online Payment (Fastest)**
- Visit: member.healthfirst.com/pay
- Log in to your member account
- Select "Make a Payment"
- Pay by credit card, debit card, or bank transfer

**Mobile App**
- Download HealthFirst app
- Navigate to "Billing"
- Secure payment processing

**Phone Payment**
- Call: 1-800-555-0199
- Automated payment: Available 24/7
- Live representative: Mon-Fri 8am-8pm

**Mail Payment**
- Make check payable to: HealthFirst Insurance
- Include your member ID on the check
- Mail to: PO Box 12345, City, State 12345

**Auto-Pay (Recommended)**
- Set up automatic monthly payments
- Never miss a payment
- Enroll at member.healthfirst.com/autopay

**Payment Confirmation:**
- Online/Phone: Immediate confirmation
- Mail: Allow 7-10 business days for processing

Do you need help making a payment now, or would you like to set up auto-pay?""",
            data={"inquiry_type": "payment"},
            confidence=0.9
        )

    async def _handle_payment_plan(self, context: AgentContext) -> AgentResponse:
        """Handle payment plan requests"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Payment Plan Options**

We understand medical bills can be unexpected. We offer flexible payment options:

**Standard Payment Plan**
- Available for balances over $200
- 3, 6, or 12-month options
- No interest charges
- Automatic monthly payments

**Hardship Program**
- For members experiencing financial difficulty
- Extended payment terms (up to 24 months)
- Possible balance reduction
- Requires income verification

**How to Enroll:**

1. **Online:**
   - Log in to member.healthfirst.com
   - Go to Billing > Payment Plans
   - Select your preferred terms
   - Set up automatic payments

2. **By Phone:**
   - Call 1-800-555-0199
   - Ask for Payment Arrangements
   - Representative will help set up your plan

**What You'll Need:**
- Member ID
- Balance amount
- Preferred monthly payment amount
- Bank account or card for auto-pay

**Important:**
- Plans require automatic payment enrollment
- Missing payments may void the agreement
- All services must be kept current

What balance amount are you looking to set up a payment plan for?""",
            data={"inquiry_type": "payment_plan"},
            confidence=0.85
        )

    async def _handle_dispute(self, context: AgentContext) -> AgentResponse:
        """Handle billing dispute inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Billing Dispute Process**

I understand you believe there may be an error on your bill. Let me help resolve this.

**Common Billing Issues:**
- Incorrect service date or provider
- Service billed that wasn't received
- Wrong amount charged
- Duplicate charges
- Coverage not applied correctly
- Wrong member billed

**To File a Dispute:**

1. **Gather Information:**
   - Date(s) of service
   - Provider name
   - Claim or invoice number
   - Description of the error
   - Supporting documentation

2. **Submit Your Dispute:**
   - **Online:** member.healthfirst.com/disputes
   - **Phone:** 1-800-555-0199
   - **Mail:** Billing Disputes, PO Box 12345

3. **What Happens Next:**
   - We'll review within 30 days
   - May contact provider for information
   - You'll receive written determination
   - Corrected bill or explanation issued

**While Under Review:**
- Balance is placed on hold
- No collection activity
- No late fees applied

**Provide these details to start your dispute:**
- What charge do you believe is incorrect?
- What date of service?
- Why do you believe it's wrong?""",
            data={"inquiry_type": "dispute"},
            requires_human=False,
            confidence=0.85
        )

    async def _handle_refund(self, context: AgentContext) -> AgentResponse:
        """Handle refund requests"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Refund Request Process**

I can help you request a refund for overpayment.

**When Refunds Apply:**
- You paid more than your responsibility
- Duplicate payment was made
- Claim was later adjusted
- Service was cancelled
- Premium overpayment

**How to Request a Refund:**

1. **Check Your Account First:**
   - Log in to member.healthfirst.com
   - Review "Billing History"
   - Check if credit was applied to future bills

2. **Submit Refund Request:**
   - **Online:** member.healthfirst.com/refunds
   - **Phone:** 1-800-555-0199
   - **Written:** Mail request with proof of payment

**Required Information:**
- Member ID
- Date of payment
- Amount paid
- Payment method used
- Proof of payment (receipt, bank statement)

**Processing Time:**
- Request review: 5-7 business days
- Refund issued: 2-4 weeks after approval
- Method: Original payment method or check

**Refund Status:**
You can check refund status online or call us.

Would you like to proceed with a refund request?""",
            data={"inquiry_type": "refund"},
            confidence=0.85
        )

    async def _handle_premium(self, context: AgentContext) -> AgentResponse:
        """Handle premium payment inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Premium Payment Information**

Your premium is your monthly insurance payment to maintain coverage.

**Premium Payment Options:**

**Automatic Payment (Recommended)**
- Bank draft (ACH) - No fees
- Credit/Debit card - Convenience fee may apply
- Set up at member.healthfirst.com/autopay

**One-Time Payment**
- Online portal
- Phone: 1-800-555-0199
- Mail (allow 10 days processing)

**Payment Due Date:**
- Typically the 1st of each month
- Grace period: 30 days for marketplace plans
- Check your billing statement for your due date

**If Payment is Late:**
- 1-30 days: Late fee may apply
- 31-60 days: Coverage at risk
- 60+ days: Coverage may terminate

**Premium Assistance Programs:**
- Advance Premium Tax Credit (marketplace)
- Cost-Sharing Reductions
- Medicaid eligibility
- State assistance programs

**Common Questions:**
- To change payment date: Call member services
- To update payment method: Online or by phone
- To get payment history: Online portal

Is there a specific premium question I can help with?""",
            data={"inquiry_type": "premium"},
            confidence=0.85
        )

    async def _handle_balance_billing(self, context: AgentContext) -> AgentResponse:
        """Handle balance billing (surprise billing) inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Balance Billing / Surprise Bill Help**

If you received a bill from a provider for more than your expected cost share, you may be protected.

**What is Balance Billing?**
When an out-of-network provider bills you for the difference between their charge and what insurance paid.

**You May Be Protected Under:**
- **No Surprises Act** (Federal law effective 1/1/2022)
- **State balance billing laws**

**Protected Situations:**
- Emergency services (any provider)
- Non-emergency services at in-network facility by OON provider
- Air ambulance from OON provider

**If You Received a Surprise Bill:**

1. **Don't Pay Immediately**
2. **Review Your EOB** - Compare to provider bill
3. **Contact Us** - We'll investigate
4. **File a Complaint** if needed

**We Can Help:**
- Review the bill for accuracy
- Determine if protections apply
- Contact the provider on your behalf
- Assist with dispute process

**Information Needed:**
- Provider bill/statement
- Date of service
- Facility where service occurred
- Your EOB for this service

**Important:**
Your cost share should be based on in-network rates for protected services.

Would you like me to help review a specific balance bill?""",
            data={"inquiry_type": "balance_billing"},
            confidence=0.85
        )

    async def _handle_general_billing(self, context: AgentContext) -> AgentResponse:
        """Handle general billing inquiries"""

        return AgentResponse(
            action=AgentAction.RESPOND,
            message="""**Billing & Payment Help**

I'm here to help with your billing questions.

**I can assist with:**

💳 **Make a Payment**
   - One-time payment
   - Set up autopay
   - Multiple payment methods

📄 **Understand Your Bill**
   - Explain charges
   - Break down your responsibility
   - Clarify EOB vs provider bill

📅 **Payment Plans**
   - Set up monthly installments
   - No-interest options available
   - Financial hardship programs

❌ **Dispute a Charge**
   - Incorrect billing
   - Services not received
   - Coverage errors

💵 **Request a Refund**
   - Overpayment recovery
   - Duplicate payment correction

📊 **Premium Payments**
   - Monthly insurance premium
   - Auto-pay setup
   - Payment history

🏥 **Surprise Bills**
   - Balance billing protection
   - Out-of-network bill review

**Quick Links:**
- Pay online: member.healthfirst.com/pay
- View bills: member.healthfirst.com/billing
- Call us: 1-800-555-0199

What billing question can I help you with today?""",
            data={"inquiry_type": "general"},
            confidence=0.8
        )
