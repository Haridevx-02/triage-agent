"""
Chat Service for Interactive Agent Conversations

Handles multi-turn conversations with specialized agents using the Groq API.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
from config import GROQ_API_KEY, GROQ_MODEL
from groq import APIStatusError
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from rag_service import build_rag_context


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    member_id: Optional[str] = None
    agent_type: str  # claims, billing, benefits, etc.
    message: str
    conversation_history: List[ChatMessage] = []
    context: Optional[Dict] = None  # Policy details, triage info, etc.


class ChatResponse(BaseModel):
    success: bool
    message: str
    agent_name: str
    requires_human: bool = False
    suggested_actions: List[str] = []
    error: Optional[str] = None


# Agent system prompts for conversational mode
AGENT_SYSTEM_PROMPTS = {
    "claims": """You are a Claims Specialist AI Agent for HealthFirst Insurance.

Your role is to help members with:
- Understanding claim status and denials
- Explaining Explanation of Benefits (EOB)
- Guiding through the claims submission process
- Helping with reimbursement questions

Guidelines:
- Be helpful, empathetic, and professional
- Use the member's policy context when available
- Provide specific, actionable guidance
- If you cannot resolve an issue, offer to escalate to a human agent
- Keep responses concise but complete
- Always offer next steps or follow-up questions""",

    "billing": """You are a Billing Resolution AI Agent for HealthFirst Insurance.

Your role is to help members with:
- Understanding bills and statements
- Payment options and payment plans
- Billing disputes and corrections
- Refund status inquiries

Guidelines:
- Be helpful, empathetic, and professional
- Explain charges clearly using member's policy details
- Offer multiple payment solutions when applicable
- If billing errors are suspected, guide through dispute process
- Keep responses concise but complete""",

    "benefits": """You are a Benefits Advisor AI Agent for HealthFirst Insurance.

Your role is to help members with:
- Coverage questions and benefit explanations
- Cost estimates for procedures
- In-network provider information
- Prescription/formulary questions

Guidelines:
- Be helpful and informative
- Use specific policy details (deductible, copays, etc.) when available
- Explain benefits in simple terms
- Provide cost estimates when possible
- Recommend in-network options to save money""",

    "prior_authorization": """You are a Prior Authorization AI Agent for HealthFirst Insurance.

Your role is to help members with:
- Understanding prior authorization requirements
- Checking authorization status
- Submitting authorization requests
- Expedited authorization for urgent cases

Guidelines:
- Explain the prior auth process clearly
- Provide timeline expectations
- Help gather required documentation
- Escalate urgent cases appropriately""",

    "member_services": """You are a Member Services AI Agent for HealthFirst Insurance.

Your role is to help members with:
- ID card requests and replacements
- Address and contact updates
- Primary care physician changes
- General account questions
- Plan information

Guidelines:
- Be friendly and helpful
- Resolve simple requests quickly
- Guide through self-service options
- Provide relevant phone numbers and websites""",

    "appeals": """You are an Appeals & Grievances AI Agent for HealthFirst Insurance.

Your role is to help members with:
- Filing appeals for denied claims
- Understanding appeal rights and timelines
- Grievance submissions
- External review requests

IMPORTANT: Appeals and grievances are sensitive matters. Always:
- Explain member rights clearly
- Provide accurate timeline information
- Document the conversation carefully
- Flag cases for human review when appropriate
- Be empathetic to member frustrations""",

    "wellness": """You are a Wellness & Outreach AI Agent for HealthFirst Insurance.

Your role is to help members with:
- Preventive care reminders
- Wellness program enrollment
- Chronic condition management
- Health assessments
- Care gap closure

Guidelines:
- Encourage healthy behaviors
- Explain preventive care benefits (100% covered!)
- Help enroll in appropriate programs
- Provide personalized recommendations based on age/gender"""
}


def get_agent_name(agent_type: str) -> str:
    """Get display name for agent type"""
    names = {
        "claims": "Claims Specialist",
        "billing": "Billing Resolution Agent",
        "benefits": "Benefits Advisor",
        "prior_authorization": "Prior Authorization Agent",
        "member_services": "Member Services Agent",
        "appeals": "Appeals & Grievances Agent",
        "wellness": "Wellness Coach"
    }
    return names.get(agent_type, "Member Services Agent")


async def chat_with_agent(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message with the appropriate agent.
    """
    if not GROQ_API_KEY:
        return ChatResponse(
            success=False,
            message="",
            agent_name=get_agent_name(request.agent_type),
            error="API key not configured"
        )

    # Get system prompt for agent type
    system_prompt = AGENT_SYSTEM_PROMPTS.get(
        request.agent_type,
        AGENT_SYSTEM_PROMPTS["member_services"]
    )

    # Add context to system prompt if available
    if request.context:
        context_str = "\n\nMember Context:\n"
        if request.context.get("member_name"):
            context_str += f"- Member Name: {request.context['member_name']}\n"
        if request.context.get("member_id"):
            context_str += f"- Member ID: {request.context['member_id']}\n"
        if request.context.get("plan_type"):
            context_str += f"- Plan Type: {request.context['plan_type']}\n"
        if request.context.get("deductible"):
            context_str += f"- Deductible: ${request.context['deductible']} (Met: ${request.context.get('deductible_met', 0)})\n"
        if request.context.get("copay_primary"):
            context_str += f"- Primary Care Copay: ${request.context['copay_primary']}\n"
        if request.context.get("copay_specialist"):
            context_str += f"- Specialist Copay: ${request.context['copay_specialist']}\n"
        if request.context.get("original_inquiry"):
            context_str += f"\nOriginal Inquiry: {request.context['original_inquiry']}\n"

        system_prompt += context_str

    rag_context = build_rag_context(request.message, member_context=system_prompt, top_k=3)
    if rag_context:
        system_prompt = rag_context

    conversation_history = [
        HumanMessage(content=msg.content) if msg.role == "user"
        else AIMessage(content=msg.content)
        for msg in request.conversation_history
    ]
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="conversation_history"),
        ("human", "{message}"),
    ])
    model = ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0.7,
        timeout=60.0,
        max_tokens=1024,
        max_retries=0,
    )
    chain = prompt_template | model | StrOutputParser()

    try:
        assistant_message = await chain.ainvoke({
            "system_prompt": system_prompt,
            "conversation_history": conversation_history,
            "message": request.message,
        })

        # Check if human escalation is needed
        requires_human = any(phrase in assistant_message.lower() for phrase in [
            "speak to a representative",
            "human agent",
            "escalate",
            "supervisor",
            "cannot resolve",
            "need to transfer"
        ])

        # Extract suggested actions (look for bullet points or numbered lists)
        suggested_actions = []
        lines = assistant_message.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '- ', '• ')):
                action = line.lstrip('0123456789.-•) ').strip()
                if len(action) > 10 and len(action) < 100:
                    suggested_actions.append(action)

        return ChatResponse(
            success=True,
            message=assistant_message,
            agent_name=get_agent_name(request.agent_type),
            requires_human=requires_human,
            suggested_actions=suggested_actions[:3]  # Limit to 3 suggestions
        )

    except APIStatusError as e:
        return ChatResponse(
            success=False,
            message="",
            agent_name=get_agent_name(request.agent_type),
            error=f"API error: {e.status_code}"
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            message="",
            agent_name=get_agent_name(request.agent_type),
            error=str(e)
        )
