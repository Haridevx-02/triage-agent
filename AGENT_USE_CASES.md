# CarePilot AI Agent Use Cases

## Overview

This document outlines the use cases for the AI agents used in the CarePilot AI member-services triage system. The workflow, routing logic, and member handling remain unchanged; only the product naming and presentation are refreshed.

---

## Agent Types and Use Cases

### 1. Claims Processing Agent (`ClaimsAgent`)

**Purpose:** Automate claims-related inquiries

| Use Case | Description | Automation Level |
|----------|-------------|-----------------|
| Claim Status Check | Look up claim status by date/provider/number | 100% Automated |
| EOB Explanation | Explain charges, payments, member responsibility | 100% Automated |
| Denial Explanation | Explain why claim was denied | 90% Automated |
| Appeal Initiation | Guide through appeal process | 80% Automated |
| Missing Documentation | Identify and request missing docs | 90% Automated |
| Reimbursement Requests | Process out-of-pocket reimbursements | 70% Automated |

**Example Interactions:**

```
Member: "Why was my claim from January 15th denied?"
Agent: [Looks up claim] → [Finds denial code] → [Explains reason]
       "Your claim was denied because prior authorization was not obtained.
        Your plan requires pre-approval for MRI services.
        You have 180 days to appeal. Would you like me to start an appeal?"
```

---

### 2. Prior Authorization Agent (`PriorAuthAgent`)

**Purpose:** Handle prior authorization lifecycle

| Use Case | Description | Automation Level |
|----------|-------------|-----------------|
| Auth Requirement Check | Determine if service needs prior auth | 100% Automated |
| Auth Status Inquiry | Check status of pending auth | 100% Automated |
| Submit Auth Request | Guide provider submission process | 80% Automated |
| Expedited Auth | Handle urgent medical authorizations | 90% Automated |
| Auth Denial Appeal | Process authorization appeals | 70% Automated |

**Example Interactions:**

```
Member: "I need an MRI approved urgently for severe back pain"
Agent: [Checks plan] → [Confirms auth required] → [Flags as urgent]
       "I've flagged this as an expedited request. For urgent cases,
        we process within 24-72 hours. Please have your doctor submit
        clinical documentation showing medical necessity."
```

---

### 3. Benefits Advisor Agent (To Be Implemented)

**Purpose:** Answer coverage and benefits questions

| Use Case | Description | Automation Level |
|----------|-------------|-----------------|
| Coverage Check | Is this service covered? | 100% Automated |
| Cost Estimation | What will I pay out of pocket? | 90% Automated |
| Provider Search | Find in-network providers | 100% Automated |
| Plan Comparison | Compare plan options | 100% Automated |
| Deductible Status | Check deductible progress | 100% Automated |

**Example Interactions:**

```
Member: "Is my colonoscopy covered? I'm turning 45."
Agent: [Checks age] → [Checks preventive benefits] → [Calculates cost]
       "Yes! Preventive colonoscopies are covered at 100% with no
        deductible when performed by an in-network provider.
        Would you like me to find in-network gastroenterologists near you?"
```

---

### 4. Billing Resolution Agent (To Be Implemented)

**Purpose:** Handle billing inquiries and disputes

| Use Case | Description | Automation Level |
|----------|-------------|-----------------|
| Bill Explanation | Explain charges and amounts due | 100% Automated |
| Payment Plan Setup | Arrange payment installments | 90% Automated |
| Billing Dispute | Investigate incorrect charges | 70% Automated |
| Refund Processing | Process overpayment refunds | 80% Automated |
| Balance Billing | Address provider balance billing | 60% Automated |

---

### 5. Member Services Agent (To Be Implemented)

**Purpose:** Handle general member requests

| Use Case | Description | Automation Level |
|----------|-------------|-----------------|
| ID Card Request | Order replacement ID cards | 100% Automated |
| Address Update | Update member demographics | 100% Automated |
| PCP Change | Process primary care physician changes | 100% Automated |
| Plan Documents | Provide plan documents and SBCs | 100% Automated |
| General Questions | Answer common questions | 90% Automated |

---

### 6. Appeals & Grievances Agent (To Be Implemented)

**Purpose:** Handle formal appeals and complaints

| Use Case | Description | Automation Level |
|----------|-------------|-----------------|
| Appeal Filing | Help file formal appeals | 70% Automated |
| Appeal Status | Track appeal progress | 100% Automated |
| Grievance Filing | Submit member complaints | 80% Automated |
| Expedited Appeal | Process urgent appeals | 60% Automated |
| External Review | Guide external review process | 50% Automated |

---

## Agent Architecture

### How Agents Work

```
┌─────────────────────────────────────────────────────────────┐
│                    Member Inquiry                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Triage System                            │
│  - Categorizes inquiry                                      │
│  - Assigns priority                                         │
│  - Identifies compliance flags                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Agent Orchestrator                         │
│  - Routes to appropriate agent                              │
│  - Manages agent handoffs                                   │
│  - Tracks conversation state                                │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │ ClaimsAgent  │ │ PriorAuth   │ │  Benefits   │
     │              │ │   Agent     │ │   Agent     │
     └──────────────┘ └──────────────┘ └──────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Response                           │
│  - Automated response to member                             │
│  - OR escalation to human agent                             │
│  - OR transfer to another agent                             │
└─────────────────────────────────────────────────────────────┘
```

### Agent Context

Each agent receives context including:
- Member ID and policy details
- Inquiry title and description
- Previous inquiry history
- Category and priority
- Compliance flags (HIPAA, CMS, etc.)

---

## Compliance Considerations

### HIPAA Compliance
- Agents never disclose PHI in responses
- Responses use general terms, not specific diagnoses
- All interactions logged for audit purposes

### CMS Regulations (Medicare/Medicaid)
- Expedited appeals: 72-hour turnaround required
- Standard appeals: 30-day turnaround required
- External review rights must be communicated

### State Mandates
- Some states require specific response times
- Agents check member's state for applicable regulations

---

## Metrics and KPIs

### Agent Performance Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Automation Rate | >70% | Inquiries resolved without human |
| First Response Time | <30 sec | Time to initial agent response |
| Resolution Time | <5 min | Time to complete resolution |
| Escalation Rate | <30% | Inquiries requiring human |
| Member Satisfaction | >4.5/5 | Post-interaction survey |
| Accuracy Rate | >95% | Correct information provided |

---

## Implementation Roadmap

### Phase 1: Foundation (Current)
- [x] Triage system with AI categorization
- [x] Policy holder database
- [x] Inquiry history tracking
- [x] Base agent architecture
- [x] Claims Agent
- [x] Prior Auth Agent

### Phase 2: Core Agents
- [ ] Benefits Advisor Agent
- [ ] Billing Resolution Agent
- [ ] Member Services Agent

### Phase 3: Advanced Features
- [ ] Appeals & Grievances Agent
- [ ] Proactive Outreach Agent
- [ ] Multi-turn conversation handling
- [ ] Integration with claims system
- [ ] Integration with provider portal

### Phase 4: Intelligence
- [ ] Predictive escalation
- [ ] Sentiment analysis
- [ ] Fraud detection
- [ ] Personalized recommendations

---

## How to Create a New Agent

1. Create a new file in `backend/agents/`
2. Inherit from `BaseAgent`
3. Implement `can_handle()` and `process()` methods
4. Register with the orchestrator

```python
from .base_agent import BaseAgent, AgentContext, AgentResponse, AgentAction

class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my_new_agent",
            description="Handles XYZ inquiries"
        )

    async def can_handle(self, context: AgentContext) -> bool:
        # Return True if this agent should handle the inquiry
        return context.current_category == "my_category"

    async def process(self, context: AgentContext) -> AgentResponse:
        # Process the inquiry and return a response
        return AgentResponse(
            action=AgentAction.RESPOND,
            message="Your response here",
            confidence=0.9
        )
```

---

## Contact

For questions about the agent system, contact the HealthFirst Insurance IT team.
