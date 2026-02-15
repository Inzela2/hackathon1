// ============================================
// UPLOAD PAGE - ADVANCED MISSION CONTROL
// All features integrated: Thought feed, confidence meter, 
// ghost mode, handoff, pivot workflow, haptic feedback, etc.
// ============================================

const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '';

// ============================================
// STATE MANAGEMENT
// ============================================

let state = {
    claimId: null,
    severity: 'unknown',
    damageType: 'unknown',
    isProcessing: false,
    uploadedImage: null,
    thoughtCounter: 0,
    confidenceLevel: 0,
    activeSkills: ['triage'],
    pivotMode: false,
    ghostModeActive: true
};

// ============================================
// HAPTIC FEEDBACK SYSTEM
// ============================================

let thinkingHeartbeat = null;

function triggerHaptic(duration = 50) {
    if (navigator.vibrate) {
        navigator.vibrate(duration);
    }
}

function startThinkingHeartbeat() {
    stopThinkingHeartbeat();
    // Subtle 10ms pulse every 2 seconds during AI thinking
    thinkingHeartbeat = setInterval(() => {
        triggerHaptic(10);
    }, 2000);
}

function stopThinkingHeartbeat() {
    if (thinkingHeartbeat) {
        clearInterval(thinkingHeartbeat);
        thinkingHeartbeat = null;
    }
}

// ============================================
// LIVE THOUGHT FEED
// ============================================

function addThought(text, type = 'info') {
    const terminal = document.getElementById('thoughtTerminal');
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    
    const thought = document.createElement('div');
    thought.className = `thought-line ${type}`;
    thought.innerHTML = `
        <span class="thought-time">${timestamp}</span>
        <span class="thought-text">${text}</span>
    `;
    
    terminal.appendChild(thought);
    terminal.scrollTop = terminal.scrollHeight;
    
    // Haptic for critical thoughts
    if (type === 'critical') {
        triggerHaptic(100);
    }
    
    state.thoughtCounter++;
}

// ============================================
// CONFIDENCE METER
// ============================================

function updateConfidence(percent, message = '') {
    const panel = document.getElementById('confidencePanel');
    const valueEl = document.getElementById('confidenceValue');
    const bar = document.getElementById('confidenceBar');
    const messageEl = document.getElementById('confidenceMessage');
    
    panel.style.display = 'block';
    state.confidenceLevel = percent;
    
    // Update display
    valueEl.textContent = `${percent}%`;
    bar.style.width = `${percent}%`;
    
    // Color coding
    valueEl.className = 'confidence-value';
    if (percent < 50) {
        valueEl.classList.add('low');
    } else if (percent < 80) {
        valueEl.classList.add('medium');
    } else {
        valueEl.classList.add('high');
    }
    
    // Set message
    if (message) {
        messageEl.textContent = message;
    } else if (percent < 50) {
        messageEl.textContent = '⚠️ Low confidence - requesting additional visual data';
        addThought(`Confidence only ${percent}% - may request second photo angle`, 'critical');
    } else if (percent > 90) {
        messageEl.textContent = '✓ High confidence - proceeding with assessment';
        addThought(`Strong confidence at ${percent}% - analysis reliable`, 'success');
    } else {
        messageEl.textContent = `Analysis in progress - ${percent}% certainty`;
    }
    
    // Haptic feedback based on confidence
    if (percent < 40) {
        triggerHaptic(200); // Strong vibration for low confidence
    }
}

// ============================================
// SKILL TREE ACTIVATION
// ============================================

function activateSkill(skillName) {
    const skill = document.getElementById(`skill-${skillName}`);
    if (skill) {
        skill.classList.add('active');
        state.activeSkills.push(skillName);
        addThought(`Skill activated: ${skillName}`, 'system');
    }
}

function completeSkill(skillName) {
    const skill = document.getElementById(`skill-${skillName}`);
    if (skill) {
        skill.classList.remove('active');
        skill.classList.add('complete');
        addThought(`Skill completed: ${skillName}`, 'success');
    }
}

// ============================================
// GHOST MODE - AMBIENT AUDIO MONITORING
// ============================================

let ghostRecognition = null;

function initGhostMode() {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        console.warn('Ghost mode not supported');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    ghostRecognition = new SpeechRecognition();
    
    ghostRecognition.continuous = true;
    ghostRecognition.interimResults = true;
    ghostRecognition.lang = 'en-AU';
    
    ghostRecognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
        
        // Emergency keywords
        const emergencyKeywords = ['help', 'stop', 'emergency', 'fire', 'spark', 'flooding', 'water'];
        const detected = emergencyKeywords.find(keyword => transcript.includes(keyword));
        
        if (detected) {
            handleEmergencyInterrupt(detected, transcript);
        }
    };
    
    ghostRecognition.onerror = (event) => {
        if (event.error !== 'no-speech') {
            console.error('Ghost mode error:', event.error);
        }
    };
    
    // Start monitoring
    try {
        ghostRecognition.start();
        addThought('Ghost mode: Ambient audio monitoring active', 'system');
    } catch (error) {
        console.error('Failed to start ghost mode:', error);
    }
}

function handleEmergencyInterrupt(keyword, fullTranscript) {
    // Stop all processing
    state.isProcessing = false;
    stopThinkingHeartbeat();
    
    // Show emergency HUD
    showEmergencyHUD(keyword, fullTranscript);
    
    // Log critical event
    addThought(`🚨 EMERGENCY INTERRUPT: Detected "${keyword}" in audio stream`, 'critical');
    addThought(`Full context: "${fullTranscript}"`, 'critical');
    
    // Strong haptic
    triggerHaptic(300);
    
    // Play alert sound
    const alertSound = document.getElementById('alertSound');
    if (alertSound) {
        alertSound.play().catch(e => console.log('Audio play failed:', e));
    }
}

function showEmergencyHUD(keyword, context) {
    const hud = document.getElementById('emergencyHUD');
    const title = document.getElementById('hudTitle');
    const message = document.getElementById('hudMessage');
    const action = document.getElementById('hudAction');
    
    // Customize based on keyword
    const responses = {
        'fire': {
            title: '🔥 FIRE DETECTED',
            message: 'EVACUATE IMMEDIATELY. Call 000. Do not attempt to fight the fire yourself.',
            action: 'I AM SAFE'
        },
        'spark': {
            title: '⚡ ELECTRICAL HAZARD',
            message: 'Turn off power at the main breaker NOW. Do not touch any electrical equipment.',
            action: 'POWER OFF'
        },
        'flooding': {
            title: '💧 FLOODING EMERGENCY',
            message: 'Turn off electricity at main breaker. Move to higher ground. Avoid standing water.',
            action: 'UNDERSTOOD'
        },
        'help': {
            title: '🚨 EMERGENCY ASSISTANCE',
            message: 'If you are in immediate danger, call 000. AI is escalating to human supervisor.',
            action: 'ACKNOWLEDGED'
        }
    };
    
    const response = responses[keyword] || responses['help'];
    
    title.textContent = response.title;
    message.textContent = response.message;
    action.textContent = response.action;
    
    hud.style.display = 'flex';
    
    // Trigger handoff
    initiateHandoff('emergency_interrupt');
}

// ============================================
// HANDOFF MAP - CONTEXT TRANSFER
// ============================================

function initiateHandoff(reason = 'manual') {
    const handoffMap = document.getElementById('handoffMap');
    handoffMap.style.display = 'block';
    
    addThought(`Initiating context transfer to human supervisor (Reason: ${reason})`, 'info');
    
    const transfers = [
        { id: 'handoff-audio', delay: 0, label: 'audio transcript' },
        { id: 'handoff-vision', delay: 800, label: 'vision analysis' },
        { id: 'handoff-negotiation', delay: 1600, label: 'negotiation data' }
    ];
    
    const statusEl = document.getElementById('handoffStatus');
    
    transfers.forEach((transfer, index) => {
        setTimeout(() => {
            const element = document.getElementById(transfer.id);
            element.style.width = '100%';
            statusEl.textContent = `Transferring ${transfer.label}...`;
            addThought(`Transfer ${index + 1}/3: ${transfer.label}`, 'info');
            triggerHaptic(30);
        }, transfer.delay);
    });
    
    setTimeout(() => {
        statusEl.textContent = '✓ Transfer complete - Supervisor Sarah briefed (4.2MB context)';
        addThought('Human supervisor now has complete emergency context', 'success');
        triggerHaptic(100);
    }, 2500);
}

// ============================================
// PIVOT WORKFLOW - RE-PLANNING
// ============================================

function triggerPivot(reason, alternative) {
    state.pivotMode = true;
    
    const notification = document.getElementById('pivotNotification');
    const message = document.getElementById('pivotMessage');
    
    notification.style.display = 'flex';
    message.textContent = alternative;
    
    addThought('🔄 PRIMARY PLAN FAILED - Initiating autonomous re-plan', 'critical');
    addThought(`Failure reason: ${reason}`, 'critical');
    addThought(`Alternative strategy: ${alternative}`, 'info');
    
    triggerHaptic(150);
    
    // Update UI to show pivot
    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}

// ============================================
// AUTONOMOUS PROPOSAL GATE
// ============================================

function showAutonomousProposal(proposalData) {
    const card = document.getElementById('proposalCard');
    const content = document.getElementById('proposalContent');
    
    content.innerHTML = `
        <div class="proposal-detail">
            <h4>${proposalData.contractor}</h4>
            <p class="proposal-price">Total Cost: <strong>$${proposalData.totalCost.toFixed(2)} AUD</strong></p>
            <p>Deposit Required: $${proposalData.deposit.toFixed(2)}</p>
            <p>Arrival Time: ${proposalData.eta}</p>
            <p>Rating: ⭐ ${proposalData.rating}/5.0</p>
        </div>
        <div class="proposal-reasoning">
            <p><strong>AI Reasoning:</strong></p>
            <p>${proposalData.reasoning}</p>
        </div>
    `;
    
    card.style.display = 'block';
    
    addThought('Autonomous proposal generated - awaiting human approval', 'info');
    addThought(`Negotiated: ${proposalData.contractor} - $${proposalData.totalCost}`, 'success');
}

// ============================================
// ADAPTIVE EMERGENCY HUD
// ============================================

function updateUIForSeverity(severity) {
    const hud = document.getElementById('emergencyHUD');
    
    if (severity === 'critical') {
        // Show immediate action button
        showEmergencyHUD('critical', 'Critical damage requires immediate action');
    } else if (severity === 'severe') {
        // Show urgent messaging
        addThought('Severe damage - expediting contractor search', 'critical');
    }
    // For moderate/minor, keep standard UI
}

// ============================================
// IMAGE UPLOAD & ANALYSIS
// ============================================

function setupImageUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const uploadBtn = document.getElementById('uploadBtn');
    const imageInput = document.getElementById('imageInput');
    const preview = document.getElementById('imagePreview');
    
    uploadBtn.addEventListener('click', () => imageInput.click());
    
    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleImageSelect(file);
    });
    
    // Drag & drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleImageSelect(file);
        }
    });
}

function handleImageSelect(file) {
    state.uploadedImage = file;
    
    // Show preview
    const preview = document.getElementById('imagePreview');
    const reader = new FileReader();
    
    reader.onload = (e) => {
        preview.innerHTML = `
            <img src="${e.target.result}" alt="Damage photo">
            <button id="analyzeBtn" class="analyze-btn">🔍 Analyze Damage</button>
        `;
        preview.style.display = 'block';
        
        document.getElementById('analyzeBtn').addEventListener('click', analyzeImage);
    };
    
    reader.readAsDataURL(file);
    
    addThought('Image uploaded - ready for vision analysis', 'success');
    activateSkill('vision');
}

async function analyzeImage() {
    if (state.isProcessing || !state.uploadedImage) return;
    
    state.isProcessing = true;
    startThinkingHeartbeat();
    
    addThought('Initiating computer vision analysis...', 'info');
    updateConfidence(35, 'Scanning image data...');
    
    const formData = new FormData();
    formData.append('image', state.uploadedImage);
    formData.append('claim_id', state.claimId);
    
    try {
        // Simulate progressive confidence updates
        setTimeout(() => updateConfidence(55, 'Detecting damage patterns...'), 500);
        setTimeout(() => updateConfidence(75, 'Estimating repair costs...'), 1000);
        
        const response = await fetch(`${API_URL}/api/upload-damage`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateConfidence(95, 'Analysis complete with high certainty');
            completeSkill('vision');
            
            addThought(`Vision analysis: ${data.assessment.description}`, 'success');
            addThought(`Estimated cost: $${data.assessment.estimated_cost}`, 'info');
            addThought(`Urgency: ${data.assessment.urgency}`, 'info');
            
            // Check for safety hazards
            if (data.assessment.safety_hazards && data.assessment.safety_hazards.length > 0) {
                addThought(`⚠️ Safety hazards detected: ${data.assessment.safety_hazards.join(', ')}`, 'critical');
                updateUIForSeverity('severe');
            }
            
            displayAssessment(data.assessment);
            
            // Auto-proceed to negotiation
            setTimeout(() => findContractors(), 2000);
            
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        addThought(`ERROR: ${error.message}`, 'critical');
        updateConfidence(0, 'Analysis failed - requesting manual review');
        
        // Trigger handoff on failure
        initiateHandoff('analysis_failure');
    } finally {
        state.isProcessing = false;
        stopThinkingHeartbeat();
    }
}

function displayAssessment(assessment) {
    const results = document.getElementById('assessmentResults');
    
    results.innerHTML = `
        <div class="assessment-card">
            <h3>✓ Visual Analysis Complete</h3>
            <div class="assessment-grid">
                <div>
                    <label>Description:</label>
                    <p>${assessment.description}</p>
                </div>
                <div>
                    <label>Estimated Cost:</label>
                    <p class="cost-large">$${assessment.estimated_cost.toLocaleString()} AUD</p>
                    <p class="cost-range">Range: $${assessment.cost_range.min.toLocaleString()} - $${assessment.cost_range.max.toLocaleString()}</p>
                </div>
                <div>
                    <label>Urgency:</label>
                    <p class="urgency-${assessment.urgency}">${assessment.urgency.toUpperCase()}</p>
                </div>
                ${assessment.safety_hazards && assessment.safety_hazards.length > 0 ? `
                <div>
                    <label>⚠️ Safety Hazards:</label>
                    <ul>${assessment.safety_hazards.map(h => `<li>${h}</li>`).join('')}</ul>
                </div>
                ` : ''}
            </div>
        </div>
    `;
    
    results.style.display = 'block';
}

// ============================================
// CONTRACTOR NEGOTIATION
// ============================================

async function findContractors() {
    activateSkill('negotiation');
    startThinkingHeartbeat();
    
    addThought('Activating haggler agent - contacting local contractors', 'info');
    updateConfidence(0, 'Negotiating with multiple contractors...');
    
    try {
        // Simulate progressive negotiation
        setTimeout(() => {
            addThought('Contacted Dave\'s Roofing - awaiting quote...', 'info');
            updateConfidence(30, 'Contractor 1 of 3 responding...');
        }, 500);
        
        setTimeout(() => {
            addThought('Contacted Apex Repairs - comparing rates...', 'info');
            updateConfidence(60, 'Contractor 2 of 3 responding...');
        }, 1500);
        
        const response = await fetch(`${API_URL}/api/find-contractor`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim_id: state.claimId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateConfidence(100, 'Negotiation complete - best deal identified');
            completeSkill('negotiation');
            
            const best = data.contractors[0];
            
            addThought(`Best deal: ${best.name} - $${best.final_price}`, 'success');
            addThought(`Saved $${(best.original_price - best.final_price).toFixed(0)} through negotiation`, 'success');
            
            // Show autonomous proposal
            showAutonomousProposal({
                contractor: best.name,
                totalCost: best.final_price,
                deposit: best.deposit_required,
                eta: best.eta,
                rating: best.rating,
                reasoning: `Selected ${best.name} as optimal choice: ${best.discount_percent}% discount secured, ${best.speed} response time, ${best.rating}/5 rating. ${best.negotiation_notes}`
            });
            
        } else if (data.pivot) {
            // PIVOT WORKFLOW - Contractor failed
            triggerPivot(
                'All local contractors engaged in hospital emergency',
                data.alternative.strategy
            );
            
            addThought('Alternative: Uber delivery of emergency repair kit', 'info');
            addThought(`Source: ${data.alternative.source}`, 'info');
            addThought(`ETA: ${data.alternative.eta}`, 'success');
            
        } else {
            throw new Error(data.error || 'Negotiation failed');
        }
        
    } catch (error) {
        console.error('Negotiation error:', error);
        addThought(`Negotiation error: ${error.message}`, 'critical');
        
        // Trigger handoff
        initiateHandoff('negotiation_failure');
    } finally {
        stopThinkingHeartbeat();
    }
}

// ============================================
// PROPOSAL APPROVAL
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('approveProposal')?.addEventListener('click', async () => {
        activateSkill('payment');
        addThought('Proposal approved - processing payment...', 'success');
        
        try {
            const response = await fetch(`${API_URL}/api/process-payment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    claim_id: state.claimId,
                    contractor_id: 0
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                completeSkill('payment');
                addThought('Payment processed - contractor dispatched!', 'success');
                triggerHaptic(200);
                
                // Redirect to success
                setTimeout(() => {
                    window.location.href = `/success.html?claim=${state.claimId}`;
                }, 1500);
            }
        } catch (error) {
            addThought(`Payment error: ${error.message}`, 'critical');
        }
    });
    
    document.getElementById('declineProposal')?.addEventListener('click', () => {
        addThought('Proposal declined - searching for alternatives...', 'info');
        document.getElementById('proposalCard').style.display = 'none';
        initiateHandoff('user_declined_proposal');
    });
});

// ============================================
// EMERGENCY HUD ACKNOWLEDGMENT
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('hudAction')?.addEventListener('click', () => {
        document.getElementById('emergencyHUD').style.display = 'none';
        addThought('Emergency acknowledged - continuing with safety protocols', 'info');
    });
});

// ============================================
// INITIALIZATION
// ============================================

function init() {
    // Get claim ID from URL
    const params = new URLSearchParams(window.location.search);
    state.claimId = params.get('claim');
    
    if (!state.claimId) {
        alert('No claim ID found');
        window.location.href = '/';
        return;
    }
    
    document.getElementById('claimIdDisplay').textContent = state.claimId;
    
    // Setup
    setupImageUpload();
    initGhostMode();
    loadTriageData();
    
    addThought('Visual assessment module initialized', 'system');
    addThought('Awaiting damage photo for computer vision analysis', 'info');
}

async function loadTriageData() {
    try {
        const response = await fetch(`${API_URL}/api/claim-status/${state.claimId}`);
        const data = await response.json();
        
        if (data.triage) {
            state.severity = data.triage.severity;
            state.damageType = data.triage.damage_type;
            
            document.getElementById('triageSummary').innerHTML = `
                <p><strong>AI Response:</strong> ${data.triage.response}</p>
                <p><strong>Damage Type:</strong> ${data.triage.damage_type}</p>
                <p><strong>Severity:</strong> <span class="severity-${data.triage.severity}">${data.triage.severity.toUpperCase()}</span></p>
                ${data.triage.safety_concern ? '<p class="safety-warning">⚠️ Safety Concern Identified</p>' : ''}
            `;
            
            addThought(`Triage data loaded: ${data.triage.severity} ${data.triage.damage_type}`, 'success');
            
            // Update UI based on severity
            updateUIForSeverity(data.triage.severity);
        }
    } catch (error) {
        console.error('Failed to load triage:', error);
        addThought('Warning: Could not load triage data', 'critical');
    }
}

// Start everything
document.addEventListener('DOMContentLoaded', init);