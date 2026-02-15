const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '';

let currentClaimId = null;
let claimCheckInterval = null;

// DOM Elements
const startClaimBtn = document.getElementById('startClaim');
const btnText = document.getElementById('btnText');
const btnIcon = document.getElementById('btnIcon');
const emergencyMessage = document.getElementById('emergencyMessage');
const phoneNumber = document.getElementById('phoneNumber');
const claimResponse = document.getElementById('claimResponse');
const claimsList = document.getElementById('claimsList');

// Agent elements
const agents = {
    empathy: document.getElementById('empathyAgent'),
    visual: document.getElementById('visualAgent'),
    haggler: document.getElementById('hagglerAgent'),
    finance: document.getElementById('financeAgent')
};

// Agent update function with smooth animations
function updateAgent(agentKey, status, thinking = '', delay = 0) {
    setTimeout(() => {
        const agent = agents[agentKey];
        if (!agent) return;
        
        const statusEl = agent.querySelector('.agent-status');
        const thinkingEl = agent.querySelector('.agent-thinking');
        
        // Remove all status classes
        agent.classList.remove('active', 'completed', 'error');
        
        if (status === 'active') {
            agent.classList.add('active');
            statusEl.textContent = '● Working';
            
            // Animated thinking text
            let dots = '';
            thinkingEl.innerHTML = `<span class="thinking-dots">${thinking}</span>`;
            
        } else if (status === 'completed') {
            statusEl.textContent = '✓ Complete';
            thinkingEl.textContent = thinking;
            
            // Brief completion highlight
            agent.classList.add('completed');
            
            setTimeout(() => {
                agent.classList.remove('active', 'completed');
                statusEl.textContent = 'Idle';
                // Keep thinking text visible for a bit longer
                setTimeout(() => {
                    thinkingEl.textContent = getAgentDefaultText(agentKey);
                }, 2000);
            }, 2500);
            
        } else if (status === 'error') {
            agent.classList.add('error');
            statusEl.textContent = '✕ Error';
            thinkingEl.textContent = thinking;
        } else {
            statusEl.textContent = 'Idle';
            thinkingEl.textContent = getAgentDefaultText(agentKey);
        }
    }, delay);
}

function getAgentDefaultText(agentKey) {
    const defaults = {
        empathy: 'Provides emotional support while triaging emergency calls and assessing severity',
        visual: 'Analyzes damage photos using computer vision to estimate repair costs',
        haggler: 'Contacts multiple contractors and negotiates the best price and arrival time',
        finance: 'Processes payments instantly and sends confirmation to all parties'
    };
    return defaults[agentKey] || '';
}

// Start Claim Handler
startClaimBtn.addEventListener('click', async () => {
    const message = emergencyMessage.value.trim();
    const phone = phoneNumber.value.trim();
    
    if (!message) {
        showNotification('Please describe your emergency', 'error');
        emergencyMessage.focus();
        return;
    }
    
    if (!phone) {
        showNotification('Please enter your phone number', 'error');
        phoneNumber.focus();
        return;
    }
    
    // Update button state
    startClaimBtn.disabled = true;
    btnIcon.textContent = '⏳';
    btnText.textContent = 'Processing Emergency...';
    
    // Activate empathy agent
    updateAgent('empathy', 'active', 'Analyzing emergency call, assessing severity, and preparing response');
    
    try {
        const response = await fetch(`${API_URL}/api/start-claim`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, phone })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentClaimId = data.claim_id;
            
            // Show empathy agent thinking process
            setTimeout(() => {
                if (data.triage && data.triage.thinking) {
                    updateAgent('empathy', 'active', 
                        `Analysis: ${data.triage.thinking}`
                    );
                }
            }, 800);
            
            // Complete empathy agent
            setTimeout(() => {
                updateAgent('empathy', 'completed', 
                    `Assessed as ${data.severity} severity. Claim #${data.claim_id} created.`
                );
                
                // Show response
                displayClaimResponse(data);
                
                // Load claims
                loadClaims();
                
                // Clear form
                emergencyMessage.value = '';
                
            }, 2000);
            
        } else {
            throw new Error(data.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        updateAgent('empathy', 'error', 'Failed to process claim. Please try again.');
        showNotification('Error: ' + error.message, 'error');
    } finally {
        setTimeout(() => {
            startClaimBtn.disabled = false;
            btnIcon.textContent = '🚀';
            btnText.textContent = 'Process Emergency Claim';
        }, 2500);
    }
});

// Display claim response
function displayClaimResponse(data) {
    claimResponse.style.display = 'block';
    claimResponse.innerHTML = `
        <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1.5rem;">
            <div style="font-size: 2.5rem;">✓</div>
            <div style="flex: 1;">
                <h3 style="margin-bottom: 0.5rem;">Claim #${data.claim_id} Started</h3>
                <p style="color: var(--text-secondary); margin: 0;">Emergency triage complete</p>
            </div>
        </div>
        
        <div style="background: white; border-radius: var(--radius-md); padding: 1.5rem; margin-bottom: 1rem;">
            <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                <strong>AI Response:</strong>
            </p>
            <p style="font-size: 1.125rem; line-height: 1.6; margin: 0;">
                "${data.response}"
            </p>
        </div>
        
        <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
            <span class="severity-badge severity-${data.severity}">
                ${data.severity} severity
            </span>
            ${data.triage.safety_concern ? 
                '<span class="severity-badge severity-critical">⚠️ Safety Concern</span>' : ''
            }
        </div>
        
        <div style="background: rgba(74,144,226,0.05); border-radius: var(--radius-md); padding: 1.5rem;">
            <p style="margin: 0 0 1rem 0; color: var(--text-secondary);">
                <strong>📸 Next Step:</strong> Upload a photo of the damage so our Visual Agent can assess the situation
            </p>
            <a href="${data.upload_link}" class="btn btn-primary" style="text-decoration: none;">
                <span>Continue to Photo Upload</span>
                <span>→</span>
            </a>
        </div>
    `;
    
    // Smooth scroll to response
    setTimeout(() => {
        claimResponse.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// Load all claims
async function loadClaims() {
    try {
        const response = await fetch(`${API_URL}/api/all-claims`);
        const data = await response.json();
        
        if (data.success && data.claims.length > 0) {
            // Sort by timestamp (newest first)
            const sortedClaims = data.claims.sort((a, b) => 
                new Date(b.timestamp) - new Date(a.timestamp)
            );
            
            claimsList.innerHTML = sortedClaims.map(claim => {
                const timeAgo = getTimeAgo(claim.timestamp);
                
                return `
                    <div class="claim-item">
                        <div class="claim-header">
                            <div>
                                <div class="claim-id">Claim #${claim.id}</div>
                                <div class="claim-time">${timeAgo}</div>
                            </div>
                            <span class="claim-status-badge ${claim.status}">
                                ${formatStatus(claim.status)}
                            </span>
                        </div>
                        
                        <p class="claim-message">${claim.initial_message}</p>
                        
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                            <span class="severity-badge severity-${claim.triage.severity}">
                                ${claim.triage.severity}
                            </span>
                            ${claim.triage.damage_type !== 'unknown' ? 
                                `<span style="display: inline-block; padding: 0.4rem 1rem; background: var(--border); border-radius: 50px; font-size: 0.75rem; font-weight: 600;">
                                    ${claim.triage.damage_type}
                                </span>` : ''
                            }
                        </div>
                        
                        ${claim.status === 'completed' && claim.contractor ? `
                            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);">
                                <p style="font-size: 0.875rem; color: var(--text-secondary);">
                                    <strong>Contractor:</strong> ${claim.contractor.name} • 
                                    <strong>ETA:</strong> ${claim.contractor.eta}
                                </p>
                            </div>
                        ` : ''}
                    </div>
                `;
            }).join('');
        } else {
            claimsList.innerHTML = `
                <p style="color: var(--text-secondary); text-align: center; padding: 3rem;">
                    No active claims yet. Start one above to see the magic happen! ✨
                </p>
            `;
        }
    } catch (error) {
        console.error('Error loading claims:', error);
    }
}

// Helper: Format status
function formatStatus(status) {
    const statusMap = {
        'triaged': 'Triaged',
        'assessed': 'Assessed',
        'negotiated': 'Negotiated',
        'completed': '✓ Completed'
    };
    return statusMap[status] || status;
}

// Helper: Time ago
function getTimeAgo(timestamp) {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now - then;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}

// Helper: Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        background: ${type === 'error' ? 'var(--error)' : 'var(--primary-blue)'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Auto-refresh claims
loadClaims();
setInterval(loadClaims, 5000);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Cmd/Ctrl + Enter to submit
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        if (document.activeElement === emergencyMessage) {
            startClaimBtn.click();
        }
    }
});

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);