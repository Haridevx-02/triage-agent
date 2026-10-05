# Aster Health Member Triage

Aster Health is a member-services triage system for health insurance operations. It uses an LLM, LangChain, and retrieval-augmented generation (RAG) to classify, prioritize, and route member inquiries with relevant policy and knowledge-base context.

## Screenshots

### Member Lookup & Support Desk
![Member Lookup](docs/images/01-member-lookup.png)
*Look up a member and view policy details alongside the inquiry form*

### Submit an Inquiry
![Submit Inquiry](docs/images/02-submit-inquiry.png)
*Provide member context and inquiry details for AI-powered triage*

### Triage Results
![Triage Results](docs/images/03-triage-results.png)
*Review the category, priority, assigned team, SLA, suggested response, and routing rationale*

### AI Agent Response
![Agent Response](docs/images/04-agent-response.png)
*See the specialized agent response for the routed inquiry*

## Features

### Core Capabilities
- **AI-Powered Triage**: Automatically categorizes and prioritizes member inquiries using Groq LLM
- **7 Specialized Agents**: Domain-specific AI agents for different inquiry types
- **Interactive Chat**: Real-time conversation with agents for follow-up questions
- **Policy Context Awareness**: Uses member's policy details for personalized responses
- **Inquiry History Tracking**: Stores and references previous inquiries for context
- **HIPAA Compliance Flags**: Identifies inquiries requiring compliance review

### Specialized AI Agents

| Agent | Handles |
|-------|---------|
| **Claims Agent** | Claim status, denials, EOBs, reimbursements |
| **Prior Authorization Agent** | Prior auth requests, status, requirements |
| **Benefits Agent** | Coverage questions, cost estimates, provider search |
| **Billing Agent** | Payments, disputes, payment plans, refunds |
| **Member Services Agent** | ID cards, address updates, PCP changes |
| **Appeals & Grievances Agent** | Appeals, grievances, external reviews |
| **Wellness Agent** | Preventive care, wellness programs, chronic care |

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI/LLM**: Groq API (LLaMA 3.3 70B)
- **Database**: SQLite (async with aiosqlite)

## Project Structure

```
ticket-triage-agent/
├── backend/
│   ├── agents/
│   │   ├── __init__.py          # Agent orchestrator factory
│   │   ├── base_agent.py        # Base agent class & orchestrator
│   │   ├── claims_agent.py      # Claims processing agent
│   │   ├── prior_auth_agent.py  # Prior authorization agent
│   │   ├── benefits_agent.py    # Benefits advisor agent
│   │   ├── billing_agent.py     # Billing resolution agent
│   │   ├── member_services_agent.py  # General member services
│   │   ├── appeals_agent.py     # Appeals & grievances agent
│   │   └── outreach_agent.py    # Wellness & outreach agent
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration settings
│   ├── models.py                # Pydantic models
│   ├── database.py              # SQLAlchemy database setup
│   ├── db_service.py            # Database operations
│   ├── grok_service.py          # Groq API integration
│   ├── triage_service.py        # Triage logic
│   ├── chat_service.py          # Interactive chat service
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── index.html               # Main HTML page
│   ├── style.css                # Styles
│   └── app.js                   # Frontend JavaScript
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── AGENT_USE_CASES.md           # Agent use cases documentation
└── README.md                    # This file
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Groq API key (get one at [console.groq.com](https://console.groq.com))

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rdekarmakar/ticket-triage-agent.git
   cd ticket-triage-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Run these commands from the backend directory on Windows
   copy ..\.env.example .env
   notepad .env
   ```
   Replace `your_groq_api_key_here` with your key from [Groq Console](https://console.groq.com/keys). Keep the variable name exactly `GROQ_API_KEY` and do not share or commit the key.

5. **Run the application**
   ```bash
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

6. **Access the application**
   - Open http://localhost:8000 in your browser
   - Click "Load Demo Data" to populate sample policy holders
   - Try looking up member ID: `HF100001`

## Usage

### Basic Workflow

1. **Lookup a Member** (optional)
   - Enter a Member ID (e.g., `HF100001`)
   - Click "Lookup" to load policy details

2. **Submit an Inquiry**
   - Enter a subject (e.g., "Claim denied for MRI")
   - Describe the issue in detail
   - Click "Analyze Inquiry"

3. **View Triage Results**
   - Category, Priority, Assigned Team
   - SLA timeframe
   - Compliance flags
   - AI-suggested response

4. **Interact with Agent**
   - See the specialized agent's detailed response
   - Ask follow-up questions in the chat
   - Get personalized guidance based on your policy

### Sample Inquiries to Test

| Inquiry Type | Sample Subject | Sample Description |
|--------------|----------------|-------------------|
| Claims | Claim denied for MRI | My claim #CLM-12345 was denied. Why? |
| Prior Auth | Need surgery approval | Doctor wants to schedule knee replacement |
| Benefits | Physical therapy coverage | How many PT sessions are covered? |
| Billing | Incorrect bill | I was charged $500 but already met deductible |
| Member Services | Lost ID card | Need a replacement insurance card |
| Appeals | Appeal denied claim | I want to appeal the MRI denial |
| Wellness | Gym reimbursement | How do I get reimbursed for gym membership? |

## API Endpoints

### Triage
```
POST /api/triage
```
Submit an inquiry for AI-powered triage and agent response.

### Chat
```
POST /api/chat
```
Send follow-up messages to continue conversation with an agent.

### Members
```
GET  /api/members/{member_id}    # Get member details
GET  /api/members                # List all members
POST /api/members                # Create new member
PUT  /api/members/{member_id}    # Update member
```

### Utilities
```
GET  /api/health                 # Health check
POST /api/seed-demo-data         # Load demo data
```

## Agent Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Inquiry                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Groq LLM (Triage)                          │
│  - Categorize inquiry                                    │
│  - Assign priority                                       │
│  - Route to team                                         │
│  - Generate initial response                             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│            Agent Orchestrator                            │
│  - Routes to specialized agent based on category         │
│  - Provides policy context                               │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│  Claims   │  │  Benefits │  │  Billing  │  ... (7 agents)
│   Agent   │  │   Agent   │  │   Agent   │
└───────────┘  └───────────┘  └───────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Detailed Agent Response                     │
│  - Personalized guidance                                 │
│  - Step-by-step instructions                             │
│  - Relevant contact info                                 │
│  - Action items                                          │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Interactive Chat                            │
│  - Follow-up questions                                   │
│  - Conversation history maintained                       │
│  - Context-aware responses                               │
└─────────────────────────────────────────────────────────┘
```

## Demo Data

The application includes demo policy holders for testing:

| Member ID | Name | Plan Type | Notes |
|-----------|------|-----------|-------|
| HF100001 | John Smith | PPO | Standard plan with dental/vision |
| HF100002 | Sarah Johnson | Medicare Advantage | $0 PCP copay |
| HF100003 | Michael Williams | HDHP | High deductible, HSA eligible |
| HF100004 | Emily Davis | HMO | Low copays, referral required |

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key | Yes |

### Customization

- **Categories**: Modify `models.py` to add/change inquiry categories
- **Teams**: Update team assignments in `models.py`
- **Agent Behavior**: Customize agent prompts in individual agent files
- **SLA Times**: Adjust SLA hours in `grok_service.py`

## Development

### Running in Development Mode
```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Testing the API
```bash
# Health check
curl http://localhost:8000/api/health

# Submit triage request
curl -X POST http://localhost:8000/api/triage \
  -H "Content-Type: application/json" \
  -d '{"title": "Claim denied", "description": "My MRI claim was denied", "member_id": "HF100001"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- AI powered by [Groq](https://groq.com/) and LLaMA 3.3 70B
- Designed for health insurance member services workflows

---

**Note**: This is a demonstration application. In production, ensure proper security measures, HIPAA compliance, and thorough testing before handling real member data.
