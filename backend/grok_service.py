import json
from config import GROQ_API_KEY, GROQ_MODEL
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

TRIAGE_PROMPT = """You are an expert health insurance ticket triage system for HealthFirst Insurance, a major US-based health insurance company. Analyze the following member/provider inquiry and provide a structured triage assessment.

**Ticket Title:** {title}
**Ticket Description:** {description}
**Member ID:** {member_id}
**Plan Type:** {plan_type}
**Submitted By:** {submitted_by}

{policy_context}

Analyze this ticket and respond with a JSON object containing:

1. "category": One of:
   - "claims" - Claim status, claim denials, EOB questions, reimbursement
   - "billing" - Premium payments, billing disputes, payment plans
   - "coverage" - Benefits questions, what's covered, coverage limits
   - "enrollment" - New enrollment, plan changes, open enrollment
   - "prior_authorization" - Pre-approval requests, auth status, medical necessity
   - "appeals_grievances" - Appeal a decision, file a complaint, dispute resolution
   - "provider_network" - In-network providers, out-of-network, provider changes
   - "pharmacy_benefits" - Prescription coverage, formulary, specialty drugs
   - "member_services" - ID cards, general questions, account updates
   - "technical_support" - Portal issues, app problems, login help
   - "hipaa_compliance" - Privacy concerns, PHI requests, data access
   - "fraud" - Suspicious activity, fraud reporting
   - "other" - Anything else

2. "priority": One of:
   - "urgent" - Life-threatening situations, emergency care denials, urgent prior auths, time-sensitive appeals (24-48 hour SLA)
   - "high" - Claim denials affecting care, prior auth delays, grievances (3-5 day SLA)
   - "medium" - Standard claims issues, coverage questions, billing disputes (7-10 day SLA)
   - "low" - General inquiries, ID card requests, informational (15-30 day SLA)

3. "assigned_team": One of:
   - "claims_processing" - Claim adjudication and processing
   - "member_services" - General member support
   - "provider_relations" - Provider network issues
   - "billing_finance" - Payment and billing issues
   - "utilization_management" - Prior authorizations, medical necessity
   - "appeals_grievances" - Appeals and complaints
   - "pharmacy_services" - Pharmacy and prescription benefits
   - "enrollment_eligibility" - Enrollment and eligibility
   - "compliance_legal" - HIPAA, regulatory, legal matters
   - "it_support" - Technical issues
   - "fraud_investigation" - Fraud cases

4. "compliance_flag": One of:
   - "none" - No special compliance consideration
   - "hipaa_review" - Contains PHI or privacy concerns
   - "state_mandate" - May involve state-specific regulations
   - "cms_regulation" - Medicare/Medicaid regulatory requirement
   - "urgent_care" - Involves emergency or urgent medical care
   - "aca_related" - Affordable Care Act related

5. "suggested_response": A professional, empathetic response to the member/provider (2-3 sentences). Use HIPAA-compliant language, don't reference specific health conditions. If member has policy details available, reference their specific coverage when relevant. If they have previous inquiries, acknowledge their history.

6. "reasoning": Brief explanation of triage decisions, including any relevant policy details or history that influenced the decision (1-2 sentences)

7. "sla_hours": Recommended resolution time in hours based on priority and regulatory requirements

8. "confidence_score": A number between 0.0 and 1.0 indicating your confidence

Important Considerations:
- Appeals have strict timelines (typically 30-60 days for standard, 72 hours for expedited)
- Prior authorizations for urgent care require expedited handling
- Medicare/Medicaid members may have additional regulatory requirements
- Always maintain HIPAA compliance in responses
- Consider member's deductible status and out-of-pocket spending when relevant
- If member has previous related inquiries, prioritize appropriately and acknowledge continuity

Respond ONLY with the JSON object, no additional text."""


async def call_groq_api(title: str, description: str, member_id: str = "Not Provided",
                        plan_type: str = "Not Specified", submitted_by: str = "Unknown",
                        policy_context: str = "") -> dict:
    """Call the Groq API to triage a health insurance ticket."""

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in environment variables")

    prompt = TRIAGE_PROMPT.format(
        title=title,
        description=description,
        member_id=member_id,
        plan_type=plan_type,
        submitted_by=submitted_by,
        policy_context=policy_context if policy_context else "No member policy details available."
    )

    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a health insurance ticket triage assistant for HealthFirst Insurance, a major US health insurer. Always respond with valid JSON only. Ensure HIPAA compliance in all responses. Use member's policy details and history when available to provide personalized, accurate triage."
        ),
        ("human", TRIAGE_PROMPT),
    ])
    model = ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0.3,
        timeout=30.0,
        max_retries=0,
    )
    chain = prompt_template | model | StrOutputParser()
    content = await chain.ainvoke({
        "title": title,
        "description": description,
        "member_id": member_id,
        "plan_type": plan_type,
        "submitted_by": submitted_by,
        "policy_context": policy_context if policy_context else "No member policy details available."
    })

    # Handle potential markdown code blocks before parsing the JSON response.
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    return json.loads(content)
