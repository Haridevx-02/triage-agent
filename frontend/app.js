const form = document.getElementById('ticketForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const historySection = document.getElementById('historySection');
const memberInfo = document.getElementById('memberInfo');
const lookupBtn = document.getElementById('lookupBtn');
const seedDataBtn = document.getElementById('seedDataBtn');
const memberLookupInput = document.getElementById('memberLookup');

// Chat state
let chatState = {
    agentType: 'member_services',
    memberId: null,
    conversationHistory: [],
    context: null,
    originalInquiry: null
};

// Member Lookup
lookupBtn.addEventListener('click', async () => {
    const memberId = memberLookupInput.value.trim();
    if (!memberId) {
        showError('Please enter a Member ID');
        return;
    }

    hideError();
    lookupBtn.textContent = 'Loading...';
    lookupBtn.disabled = true;

    try {
        const response = await fetch(`/api/members/${memberId}`);

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Member not found. Try loading demo data first.');
            }
            throw new Error('Failed to lookup member');
        }

        const data = await response.json();
        displayMemberInfo(data);

        // Auto-fill member ID in the form
        document.getElementById('member_id').value = memberId;

        // Set plan type if available
        if (data.member.plan_type) {
            const planSelect = document.getElementById('plan_type');
            for (let option of planSelect.options) {
                if (option.value === data.member.plan_type) {
                    option.selected = true;
                    break;
                }
            }
        }

        // Show inquiry history
        if (data.recent_inquiries && data.recent_inquiries.length > 0) {
            displayInquiryHistory(data.recent_inquiries);
        } else {
            historySection.classList.add('hidden');
        }

    } catch (error) {
        showError(error.message);
        memberInfo.classList.add('hidden');
        historySection.classList.add('hidden');
    } finally {
        lookupBtn.textContent = 'Lookup';
        lookupBtn.disabled = false;
    }
});

// Seed Demo Data
seedDataBtn.addEventListener('click', async () => {
    seedDataBtn.textContent = 'Loading...';
    seedDataBtn.disabled = true;

    try {
        const response = await fetch('/api/seed-demo-data', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            alert(data.message + '\n\nTry looking up: HF100001, HF100002, HF100003, or HF100004');
        }
    } catch (error) {
        showError('Failed to seed demo data');
    } finally {
        seedDataBtn.textContent = 'Load Demo Data';
        seedDataBtn.disabled = false;
    }
});

function displayMemberInfo(data) {
    const member = data.member;

    memberInfo.innerHTML = `
        <div class="member-header">
            <span class="member-name">${member.first_name} ${member.last_name}</span>
            <span class="member-status ${member.policy_status}">${member.policy_status}</span>
        </div>
        <div class="member-details">
            <div class="member-detail">
                <div class="member-detail-label">Member ID</div>
                <div class="member-detail-value">${member.member_id}</div>
            </div>
            <div class="member-detail">
                <div class="member-detail-label">Plan Type</div>
                <div class="member-detail-value">${member.plan_type}</div>
            </div>
            <div class="member-detail">
                <div class="member-detail-label">Effective Date</div>
                <div class="member-detail-value">${member.effective_date || 'N/A'}</div>
            </div>
        </div>
        <div class="coverage-grid">
            <div class="coverage-item">
                <div class="coverage-label">Deductible</div>
                <div class="coverage-value">$${member.deductible.toLocaleString()}</div>
                <div class="coverage-label">Met: $${member.deductible_met.toLocaleString()}</div>
            </div>
            <div class="coverage-item">
                <div class="coverage-label">Out-of-Pocket Max</div>
                <div class="coverage-value">$${member.out_of_pocket_max.toLocaleString()}</div>
                <div class="coverage-label">Met: $${member.out_of_pocket_met.toLocaleString()}</div>
            </div>
            <div class="coverage-item">
                <div class="coverage-label">Primary Copay</div>
                <div class="coverage-value">$${member.copay_primary}</div>
            </div>
            <div class="coverage-item">
                <div class="coverage-label">Specialist Copay</div>
                <div class="coverage-value">$${member.copay_specialist}</div>
            </div>
        </div>
        <div class="coverage-grid" style="margin-top: 0.5rem;">
            <div class="coverage-item">
                <div class="coverage-label">Dental</div>
                <div class="coverage-value">${member.has_dental ? 'Yes' : 'No'}</div>
            </div>
            <div class="coverage-item">
                <div class="coverage-label">Vision</div>
                <div class="coverage-value">${member.has_vision ? 'Yes' : 'No'}</div>
            </div>
            <div class="coverage-item">
                <div class="coverage-label">Pharmacy</div>
                <div class="coverage-value">${member.has_pharmacy ? 'Yes' : 'No'}</div>
            </div>
            <div class="coverage-item">
                <div class="coverage-label">Inquiries</div>
                <div class="coverage-value">${data.inquiry_count}</div>
            </div>
        </div>
    `;

    memberInfo.classList.remove('hidden');
}

function displayInquiryHistory(inquiries) {
    const historyDiv = document.getElementById('inquiryHistory');

    if (inquiries.length === 0) {
        historyDiv.innerHTML = '<div class="no-history">No previous inquiries found</div>';
    } else {
        historyDiv.innerHTML = inquiries.map(inq => `
            <div class="inquiry-item">
                <div class="inquiry-header">
                    <span class="inquiry-title">${inq.title}</span>
                    <span class="inquiry-date">${inq.created_at ? new Date(inq.created_at).toLocaleDateString() : 'N/A'}</span>
                </div>
                <div class="inquiry-meta">
                    <span class="inquiry-tag">${formatLabel(inq.category)}</span>
                    <span class="inquiry-tag priority-${inq.priority}">${formatLabel(inq.priority)}</span>
                    <span class="inquiry-tag">${formatLabel(inq.status)}</span>
                </div>
            </div>
        `).join('');
    }

    historySection.classList.remove('hidden');
}

// Form Submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();
    const member_id = document.getElementById('member_id').value.trim() || null;
    const plan_type = document.getElementById('plan_type').value || null;
    const submitted_by = document.getElementById('submitted_by').value.trim() || null;

    setLoading(true);
    hideResults();
    hideError();

    try {
        const response = await fetch('/api/triage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, description, member_id, plan_type, submitted_by }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to triage inquiry');
        }

        if (data.success && data.triage) {
            displayResults(data.triage, data.agent_response);

            // Refresh member history if member_id was provided
            if (member_id) {
                try {
                    const historyResponse = await fetch(`/api/members/${member_id}/inquiries`);
                    if (historyResponse.ok) {
                        const historyData = await historyResponse.json();
                        displayInquiryHistory(historyData.inquiries);
                    }
                } catch (e) {
                    // Ignore history refresh errors
                }
            }
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    btnText.classList.toggle('hidden', isLoading);
    btnLoader.classList.toggle('hidden', !isLoading);
}

function displayResults(triage, agentResponse) {
    document.getElementById('resultCategory').textContent = formatLabel(triage.category);

    const priorityEl = document.getElementById('resultPriority');
    priorityEl.textContent = formatLabel(triage.priority);
    priorityEl.className = 'result-value priority-' + triage.priority;

    document.getElementById('resultTeam').textContent = formatLabel(triage.assigned_team);

    const slaEl = document.getElementById('resultSLA');
    slaEl.textContent = formatSLA(triage.sla_hours);

    const complianceEl = document.getElementById('resultCompliance');
    complianceEl.textContent = formatLabel(triage.compliance_flag);
    complianceEl.className = 'result-value compliance-' + triage.compliance_flag;

    const confidence = Math.round(triage.confidence_score * 100);
    document.getElementById('resultConfidence').textContent = confidence + '%';

    document.getElementById('suggestedResponse').textContent = triage.suggested_response;
    document.getElementById('reasoning').textContent = triage.reasoning;

    // Display agent response if available
    const agentSection = document.getElementById('agentResponseSection');
    if (agentResponse) {
        document.getElementById('agentName').textContent = agentResponse.agent_name;
        document.getElementById('agentAction').textContent = formatLabel(agentResponse.action);
        document.getElementById('agentConfidence').textContent =
            'Confidence: ' + Math.round(agentResponse.confidence * 100) + '%';

        // Show/hide human review badge
        const humanReviewEl = document.getElementById('agentHumanReview');
        if (agentResponse.requires_human) {
            humanReviewEl.classList.remove('hidden');
        } else {
            humanReviewEl.classList.add('hidden');
        }

        // Render agent message with markdown-like formatting
        document.getElementById('agentMessage').innerHTML = formatAgentMessage(agentResponse.message);

        // Initialize chat for follow-up questions
        const memberId = document.getElementById('member_id').value.trim() || null;
        const originalInquiry = document.getElementById('title').value + ': ' + document.getElementById('description').value;
        initializeChat(triage.category, memberId, originalInquiry);

        agentSection.classList.remove('hidden');
    } else {
        agentSection.classList.add('hidden');
    }

    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function formatAgentMessage(message) {
    if (!message) return '-';

    // Convert markdown-like formatting to HTML
    return message
        // Bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Headers (lines starting with **)
        .replace(/^(\*\*[^*]+\*\*)/gm, '<h4>$1</h4>')
        // Line breaks
        .replace(/\n/g, '<br>')
        // Bullet points
        .replace(/^- (.*?)(<br>|$)/gm, '<li>$1</li>')
        // Checkmarks
        .replace(/✓/g, '<span class="checkmark">✓</span>')
        // Tables (basic)
        .replace(/\|([^|]+)\|([^|]+)\|/g, '<div class="table-row"><span>$1</span><span>$2</span></div>');
}

function formatLabel(value) {
    if (!value) return '-';
    return value
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatSLA(hours) {
    if (hours < 24) {
        return hours + ' hours';
    } else if (hours < 48) {
        return '1 day';
    } else {
        const days = Math.round(hours / 24);
        return days + ' days';
    }
}

function hideResults() {
    resultsSection.classList.add('hidden');
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    errorSection.classList.remove('hidden');
}

function hideError() {
    errorSection.classList.add('hidden');
}

// ============== Chat Functionality ==============

const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');
const chatMessages = document.getElementById('chatMessages');

// Map triage category to agent type
function getAgentType(category) {
    const mapping = {
        'claims': 'claims',
        'billing': 'billing',
        'coverage': 'benefits',
        'enrollment': 'member_services',
        'prior_authorization': 'prior_authorization',
        'appeals_grievances': 'appeals',
        'provider_network': 'benefits',
        'pharmacy_benefits': 'benefits',
        'member_services': 'member_services',
        'technical_support': 'member_services',
        'hipaa_compliance': 'appeals',
        'fraud': 'appeals',
        'wellness': 'wellness',
        'other': 'member_services'
    };
    return mapping[category] || 'member_services';
}

// Initialize chat after triage
function initializeChat(triageCategory, memberId, originalInquiry) {
    chatState = {
        agentType: getAgentType(triageCategory),
        memberId: memberId,
        conversationHistory: [],
        context: { original_inquiry: originalInquiry },
        originalInquiry: originalInquiry
    };

    // Clear previous chat messages
    chatMessages.innerHTML = '';

    // Add welcome message
    addChatMessage('assistant', `I'm here to help with your inquiry. Feel free to ask follow-up questions!`);
}

// Add message to chat UI
function addChatMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'chat-message-content';

    if (role === 'assistant') {
        contentDiv.innerHTML = formatAgentMessage(content);
    } else {
        contentDiv.textContent = content;
    }

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send chat message
async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message to UI
    addChatMessage('user', message);
    chatInput.value = '';

    // Disable input while processing
    chatInput.disabled = true;
    sendChatBtn.disabled = true;
    sendChatBtn.textContent = '...';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                member_id: chatState.memberId,
                agent_type: chatState.agentType,
                message: message,
                conversation_history: chatState.conversationHistory,
                context: chatState.context
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to send message');
        }

        if (data.success) {
            // Add to conversation history
            chatState.conversationHistory.push(
                { role: 'user', content: message },
                { role: 'assistant', content: data.message }
            );

            // Add assistant response to UI
            addChatMessage('assistant', data.message);

            // Show human review indicator if needed
            if (data.requires_human) {
                addChatMessage('assistant', '⚠️ This conversation has been flagged for human review. A representative will follow up with you.');
            }
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    } catch (error) {
        addChatMessage('assistant', `Sorry, I encountered an error: ${error.message}. Please try again.`);
    } finally {
        chatInput.disabled = false;
        sendChatBtn.disabled = false;
        sendChatBtn.textContent = 'Send';
        chatInput.focus();
    }
}

// Event listeners for chat
sendChatBtn.addEventListener('click', sendChatMessage);

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
});
