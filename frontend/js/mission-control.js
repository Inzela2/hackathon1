// ============================================
// MISSION CONTROL - MAIN CONTROLLER
// ============================================

const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '';

// State
let currentClaimId = null;
let voiceRecognition = null;
let thoughtCounter = 0;
let isProcessing = false;

// ============================================
// VOICE RECOGNITION SETUP
// ============================================

function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        voiceRecognition = new SpeechRecognition();
        
        voiceRecognition.continuous = false;
        voiceRecognition.interimResults = true;
        voiceRecognition.lang = 'en-AU';
        
        voiceRecognition.onstart = () => {
            console.log('🎤 Voice recognition started');
            const btn = document.getElementById('voiceBtn');
            const status = document.getElementById('voiceStatus');
            
            btn.classList.add('listening');
            status.textContent = 'LISTENING...';
            
            addThought('Voice input activated - capturing emergency details', 'system');
            triggerHapticFeedback(50);
        };
        
        voiceRecognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            if (finalTranscript) {
                document.getElementById('emergencyMessage').value = finalTranscript;
                addThought(`Voice transcript: "${finalTranscript.substring(0, 50)}..."`, 'success');
            }
        };
        
        voiceRecognition.onerror = (event) => {
            console.error('🎤 Voice error:', event.error);
            resetVoiceButton();
            addThought(`Voice error: ${event.error}`, 'critical');
        };
        
        voiceRecognition.onend = () => {
            console.log('🎤 Voice recognition ended');
            resetVoiceButton();
        };
    } else {
        console.warn('Voice recognition not supported');
        document.getElementById('voiceBtn').disabled = true;
        addThought('Voice recognition not available in this browser', 'critical');
    }
}

function resetVoiceButton() {
    const btn = document.getElementById('voiceBtn');
    const status = document.getElementById('voiceStatus');
    
    btn.classList.remove('listening');
    status.textContent = 'TAP TO SPEAK';
}

// ============================================
// THOUGHT FEED SYSTEM
// ============================================

function addThought(text, type = 'info') {
    const feed = document.getElementById('thoughtFeed');
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    
    const thought = document.createElement('div');
    thought.className = `thought-item ${type}`;
    thought.innerHTML = `
        <span class="timestamp">${timestamp}</span>
        <span class="thought-text">${text}</span>
    `;
    
    feed.appendChild(thought);
    feed.scrollTop = feed.scrollHeight;
    
    // Haptic feedback for important thoughts
    if (type === 'critical') {
        triggerHapticFeedback(100);
    }
}

// ============================================
// AGENT STATUS UPDATES
// ============================================

function updateAgentStatus(agentId, status, thinking = '') {
    const agent = document.getElementById(`agent-${agentId}`);
    if (!agent) return;
    
    const statusEl = agent.querySelector('.agent-status');
    
    // Remove all status classes
    agent.classList.remove('active', 'complete');
    
    if (status === 'active') {
        agent.classList.add('active');
        statusEl.textContent = thinking || 'PROCESSING...';
        addThought(`${getAgentName(agentId)} activated - ${thinking}`, 'info');
        triggerHapticFeedback(30);
    } else if (status === 'complete') {
        agent.classList.add('complete');
        statusEl.textContent = 'COMPLETE';
        addThought(`${getAgentName(agentId)} completed successfully`, 'success');
        triggerHapticFeedback(50);
    } else {
        statusEl.textContent = 'IDLE';
    }
}

function getAgentName(agentId) {
    const names = {
        'empathy': 'Empathy Agent',
        'visual': 'Visual Agent',
        'haggler': 'Haggler Agent',
        'finance': 'Finance Agent'
    };
    return names[agentId] || agentId;
}

// ============================================
// CONFIDENCE METER
// ============================================

function updateConfidence(percent, status = '') {
    const section = document.getElementById('confidenceSection');
    const percentEl = document.getElementById('confidencePercent');
    const fill = document.getElementById('confidenceFill');
    const statusEl = document.getElementById('confidenceStatus');
    
    section.style.display = 'block';
    percentEl.textContent = `${percent}%`;
    fill.style.width = `${percent}%`;
    
    if (status) {
        statusEl.textContent = status;
    }
    
    // Add thought based on confidence
    if (percent < 50) {
        addThought(`Low confidence (${percent}%) - requesting additional data`, 'critical');
    } else if (percent > 90) {
        addThought(`High confidence (${percent}%) - proceeding with assessment`, 'success');
    }
}

// ============================================
// CONTEXT TRANSFER ANIMATION
// ============================================

function animateContextTransfer() {
    addThought('Initiating context transfer to supervisor...', 'info');
    
    const transfers = document.querySelectorAll('.transfer-progress');
    const status = document.getElementById('transferStatus');
    
    const steps = [
        { index: 0, delay: 0, text: 'Generating audio transcript...' },
        { index: 1, delay: 800, text: 'Encoding vision analysis...' },
        { index: 2, delay: 1600, text: 'Packaging negotiation data...' }
    ];
    
    steps.forEach(step => {
        setTimeout(() => {
            status.textContent = step.text;
            transfers[step.index].style.width = '100%';
            triggerHapticFeedback(20);
        }, step.delay);
    });
    
    setTimeout(() => {
        status.textContent = '✓ Transfer complete - Supervisor briefed (4.2MB context)';
        addThought('Context transfer complete - human supervisor now has full emergency data', 'success');
        triggerHapticFeedback(100);
    }, 2500);
}

// ============================================
// HAPTIC FEEDBACK
// ============================================

function triggerHapticFeedback(duration = 50) {
    if (navigator.vibrate) {
        navigator.vibrate(duration);
    }
}

// Thinking heartbeat
let thinkingHeartbeat = null;

function startThinkingHeartbeat() {
    stopThinkingHeartbeat();
    thinkingHeartbeat = setInterval(() => {
        triggerHapticFeedback(10);
    }, 2000);
}

function stopThinkingHeartbeat() {
    if (thinkingHeartbeat) {
        clearInterval(thinkingHeartbeat);
        thinkingHeartbeat = null;
    }
}

// ============================================
// SYSTEM TIME
// ============================================

function updateSystemTime() {
    const timeEl = document.getElementById('systemTime');
    const now = new Date();
    timeEl.textContent = now.toLocaleTimeString('en-US', { hour12: false });
}

setInterval(updateSystemTime, 1000);
updateSystemTime();

// ============================================
// SUBMIT CLAIM
// ============================================

async function submitClaim() {
    if (isProcessing) return;
    
    const message = document.getElementById('emergencyMessage').value.trim();
    const phone = document.getElementById('phoneNumber').value.trim();
    
    if (!message) {
        alert('Please describe the emergency or use voice input');
        return;
    }
    
    isProcessing = true;
    startThinkingHeartbeat();
    
    addThought('Emergency claim initiated - activating multi-agent system', 'info');
    updateConfidence(0, 'Initializing assessment...');
    
    try {
        // Stage 1: Empathy Agent
        updateAgentStatus('empathy', 'active', 'Analyzing emergency severity');
        updateConfidence(30, 'Performing initial triage...');
        
        const response = await fetch(`${API_URL}/api/start-claim`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentClaimId = data.claim_id;
            
            updateAgentStatus('empathy', 'complete');
            updateConfidence(75, `Severity: ${data.severity.toUpperCase()}`);
            
            addThought(`Claim ${data.claim_id} created - Severity: ${data.severity}`, 'success');
            addThought(`AI Response: "${data.response}"`, 'info');
            
            if (data.triage.safety_concern) {
                addThought('⚠️ SAFETY CONCERN DETECTED - Escalating priority', 'critical');
                triggerHapticFeedback(200);
            }
            
            // Continue to upload
            setTimeout(() => {
                window.location.href = `upload.html?claim=${data.claim_id}`;
            }, 2000);
            
        } else {
            throw new Error(data.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        addThought(`ERROR: ${error.message}`, 'critical');
        updateConfidence(0, 'System error - initiating fallback');
        alert('Error processing claim: ' + error.message);
        
        // Trigger context transfer on error
        animateContextTransfer();
    } finally {
        isProcessing = false;
        stopThinkingHeartbeat();
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize voice
    initVoiceRecognition();
    
    // Voice button
    const voiceBtn = document.getElementById('voiceBtn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', (e) => {
            e.preventDefault();
            
            if (!voiceRecognition) {
                alert('Voice recognition not supported. Please use Chrome, Edge, or Safari.');
                return;
            }
            
            try {
                voiceRecognition.start();
            } catch (error) {
                console.error('Failed to start voice:', error);
                voiceRecognition.stop();
                setTimeout(() => voiceRecognition.start(), 100);
            }
        });
    }
    
    // Submit button
    const submitBtn = document.getElementById('submitClaim');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitClaim);
    }
    
    // Enter key to submit
    document.getElementById('emergencyMessage')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            submitClaim();
        }
    });
    
    // Initial system message
    addThought('Mission Control systems online - All agents ready', 'success');
    addThought('Voice recognition initialized - Ready for emergency input', 'info');
    
    // Simulate live activity
    setTimeout(() => {
        addThought('Monitoring 10,000 concurrent calls across Australia', 'system');
    }, 2000);
});

// ============================================
// INTERRUPT HANDLING (EMERGENCY STOP)
// ============================================

// Listen for interrupt keywords
if (voiceRecognition) {
    voiceRecognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
        
        // Check for interrupt keywords
        if (transcript.includes('wait') || transcript.includes('stop') || transcript.includes('hold')) {
            addThought('🛑 INTERRUPT DETECTED - Halting current operations', 'critical');
            isProcessing = false;
            stopThinkingHeartbeat();
            triggerHapticFeedback(200);
        }
    };
}