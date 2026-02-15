const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '';

// Get claim ID from URL
const urlParams = new URLSearchParams(window.location.search);
const claimId = urlParams.get('claim');

const photoInput = document.getElementById('photoInput');
const uploadZone = document.getElementById('uploadZone');
const preview = document.getElementById('preview');
const previewImage = document.getElementById('previewImage');
const uploadBtn = document.getElementById('uploadBtn');
const claimInfo = document.getElementById('claimInfo');
const analysisResult = document.getElementById('analysisResult');

let selectedFile = null;

// Load claim info
if (claimId) {
    loadClaimInfo();
} else {
    claimInfo.innerHTML = `
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span style="font-size: 2rem;">⚠️</span>
            <div>
                <strong>Invalid Claim ID</strong>
                <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary);">
                    Please start a new claim from the <a href="index.html" style="color: var(--primary-blue);">dashboard</a>
                </p>
            </div>
        </div>
    `;
    uploadZone.style.display = 'none';
}

async function loadClaimInfo() {
    try {
        const response = await fetch(`${API_URL}/api/claim-status/${claimId}`);
        const data = await response.json();
        
        if (data.success) {
            claimInfo.innerHTML = `
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <span style="font-size: 2rem;">📋</span>
                    <div style="flex: 1;">
                        <strong style="font-size: 1.125rem;">Claim #${data.claim.id}</strong>
                        <p style="margin: 0.5rem 0; color: var(--text-secondary);">
                            ${data.claim.initial_message}
                        </p>
                        <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
                            <span class="severity-badge severity-${data.claim.triage.severity}">
                                ${data.claim.triage.severity}
                            </span>
                            ${data.claim.triage.damage_type !== 'unknown' ? 
                                `<span style="display: inline-block; padding: 0.4rem 1rem; background: white; border: 1px solid var(--border); border-radius: 50px; font-size: 0.75rem; font-weight: 600;">
                                    ${data.claim.triage.damage_type}
                                </span>` : ''
                            }
                        </div>
                    </div>
                </div>
            `;
        } else {
            throw new Error('Claim not found');
        }
    } catch (error) {
        claimInfo.innerHTML = `
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 2rem;">❌</span>
                <div>
                    <strong>Error Loading Claim</strong>
                    <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary);">
                        ${error.message}
                    </p>
                </div>
            </div>
        `;
        uploadZone.style.display = 'none';
    }
}

// Drag and drop
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
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Photo input change
photoInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
});

// Handle file
function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    selectedFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        preview.style.display = 'block';
        uploadZone.style.display = 'none';
        
        // Auto-scroll to preview
        setTimeout(() => {
            preview.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    };
    reader.readAsDataURL(file);
}

// Upload and analyze
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Please select a photo first');
        return;
    }
    
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = `
        <span class="loading"></span>
        <span>Analyzing with AI Vision...</span>
    `;
    
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('claim_id', claimId);
    
    try {
        const response = await fetch(`${API_URL}/api/upload-damage`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAssessment(data.assessment);
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        alert('Error analyzing photo: ' + error.message);
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `<span>🔍</span><span>Analyze Damage</span>`;
    }
});

// Display assessment
function displayAssessment(assessment) {
    analysisResult.style.display = 'block';
    analysisResult.innerHTML = `
        <div class="card" style="background: linear-gradient(135deg, rgba(74,144,226,0.05) 0%, rgba(108,92,231,0.05) 100%); border: 2px solid var(--primary-blue);">
            <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1.5rem;">
                <span style="font-size: 2.5rem;">✓</span>
                <div>
                    <h3 style="margin-bottom: 0.5rem;">Visual Analysis Complete</h3>
                    <p style="color: var(--text-secondary); margin: 0;">AI-powered damage assessment</p>
                </div>
            </div>
            
            <div style="background: white; border-radius: var(--radius-md); padding: 1.5rem; margin-bottom: 1.5rem;">
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 0.5rem;">
                    <strong>Description:</strong>
                </p>
                <p style="line-height: 1.6; margin: 0;">
                    ${assessment.description}
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                <div style="background: white; padding: 1.5rem; border-radius: var(--radius-md);">
                    <div style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 0.5rem;">
                        Estimated Cost
                    </div>
                    <div style="font-size: 2rem; font-weight: 800; color: var(--primary-blue);">
                        $${assessment.estimated_cost.toLocaleString()}
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.25rem;">
                        ${assessment.cost_range.min.toLocaleString()} - ${assessment.cost_range.max.toLocaleString()} AUD
                    </div>
                </div>
                
                <div style="background: white; padding: 1.5rem; border-radius: var(--radius-md);">
                    <div style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 0.5rem;">
                        Urgency Level
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; text-transform: capitalize;">
                        ${assessment.urgency}
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.25rem;">
                        Required: ${assessment.required_trade}
                    </div>
                </div>
            </div>
            
            ${assessment.safety_hazards && assessment.safety_hazards.length > 0 ? `
                <div style="background: #FEF3C7; border-left: 4px solid #F59E0B; padding: 1.5rem; border-radius: var(--radius-md); margin-bottom: 1.5rem;">
                    <strong style="color: #92400E; display: block; margin-bottom: 0.5rem;">
                        ⚠️ Safety Hazards Detected:
                    </strong>
                    <ul style="margin: 0; padding-left: 1.5rem; color: #92400E;">
                        ${assessment.safety_hazards.map(h => `<li>${h}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            <div style="background: rgba(74,144,226,0.1); border-radius: var(--radius-md); padding: 1.5rem;">
                <p style="margin: 0 0 1rem 0; color: var(--text-primary);">
                    <strong>Next:</strong> Our Negotiation Agent will now contact local contractors to get you the best deal
                </p>
                <button id="findContractorBtn" class="btn btn-primary">
                    <span>🔍</span>
                    <span>Find & Negotiate with Contractors</span>
                </button>
            </div>
        </div>
    `;
    
    // Scroll to result
    setTimeout(() => {
        analysisResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
    
    // Add event listener
    document.getElementById('findContractorBtn').addEventListener('click', findContractor);
}

// Find contractor
async function findContractor() {
    const btn = document.getElementById('findContractorBtn');
    btn.disabled = true;
    btn.innerHTML = `
        <span class="loading"></span>
        <span>Negotiating with contractors...</span>
    `;
    
    try {
        const response = await fetch(`${API_URL}/api/find-contractor`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim_id: claimId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayNegotiation(data.negotiation);
        } else {
            throw new Error(data.error || 'Negotiation failed');
        }
        
    } catch (error) {
        alert('Error finding contractor: ' + error.message);
        btn.disabled = false;
        btn.innerHTML = `<span>🔍</span><span>Find & Negotiate with Contractors</span>`;
    }
}

// Display negotiation results
function displayNegotiation(negotiation) {
    const resultHTML = `
        <div class="card" style="margin-top: 2rem; background: linear-gradient(135deg, rgba(108,92,231,0.05) 0%, rgba(74,144,226,0.05) 100%); border: 2px solid var(--accent-purple);">
            <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1.5rem;">
                <span style="font-size: 2.5rem;">💼</span>
                <div>
                    <h3 style="margin-bottom: 0.5rem;">Negotiation Complete</h3>
                    <p style="color: var(--text-secondary); margin: 0;">
                        ${negotiation.negotiation_summary}
                    </p>
                </div>
            </div>
            
            <div style="display: grid; gap: 1rem;">
                ${negotiation.contractors.map((contractor, index) => `
                    <div class="contractor-card ${index === 0 ? 'selected' : ''}" data-index="${index}">
                        <div class="contractor-header">
                            <div>
                                <div class="contractor-name">${contractor.name}</div>
                                <div class="contractor-rating">⭐ ${contractor.rating}/5.0</div>
                            </div>
                            <div class="contractor-price">$${contractor.final_price.toLocaleString()}</div>
                        </div>
                        
                        <div class="contractor-details">
                            <div class="contractor-detail">
                                <span class="contractor-detail-label">Arrival Time</span>
                                <div class="contractor-detail-value">${contractor.eta}</div>
                            </div>
                            <div class="contractor-detail">
                                <span class="contractor-detail-label">Deposit Required</span>
                                <div class="contractor-detail-value">$${contractor.deposit_required.toLocaleString()}</div>
                            </div>
                            <div class="contractor-detail">
                                <span class="contractor-detail-label">You Save</span>
                                <div class="contractor-detail-value" style="color: var(--success);">
                                    ${contractor.discount_percent}%
                                </div>
                            </div>
                        </div>
                        
                        <div class="contractor-notes">
                            💡 ${contractor.negotiation_notes}
                        </div>
                        
                        ${index === 0 ? `
                            <button class="btn btn-primary" style="margin-top: 1rem;" onclick="processPayment(${index})">
                                <span>💳</span>
                                <span>Confirm & Pay Deposit ($${contractor.deposit_required.toLocaleString()})</span>
                            </button>
                        ` : `
                            <button class="btn btn-secondary" style="margin-top: 1rem;" onclick="selectContractor(${index})">
                                <span>Select This Contractor</span>
                            </button>
                        `}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    analysisResult.insertAdjacentHTML('beforeend', resultHTML);
    
    // Scroll to negotiation results
    setTimeout(() => {
        document.querySelector('.contractor-card').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest' 
        });
    }, 100);
}

// Select contractor
window.selectContractor = function(index) {
    document.querySelectorAll('.contractor-card').forEach((card, i) => {
        card.classList.toggle('selected', i === index);
        
        const btn = card.querySelector('button');
        const contractor = card.querySelector('.contractor-price').textContent.replace(/[^0-9]/g, '');
        const deposit = card.querySelector('.contractor-detail-value').textContent.replace(/[^0-9]/g, '');
        
        if (i === index) {
            btn.className = 'btn btn-primary';
            btn.style.marginTop = '1rem';
            btn.innerHTML = `
                <span>💳</span>
                <span>Confirm & Pay Deposit ($${parseInt(deposit).toLocaleString()})</span>
            `;
            btn.onclick = () => processPayment(index);
        } else {
            btn.className = 'btn btn-secondary';
            btn.style.marginTop = '1rem';
            btn.innerHTML = '<span>Select This Contractor</span>';
            btn.onclick = () => selectContractor(i);
        }
    });
}

// Process payment
window.processPayment = async function(contractorIndex) {
    const btn = event.target.closest('button');
    btn.disabled = true;
    btn.innerHTML = `
        <span class="loading"></span>
        <span>Processing payment...</span>
    `;
    
    try {
        const response = await fetch(`${API_URL}/api/process-payment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                claim_id: claimId,
                contractor_id: contractorIndex
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayCompletion(data);
        } else {
            throw new Error(data.error || 'Payment failed');
        }
        
    } catch (error) {
        alert('Error processing payment: ' + error.message);
        btn.disabled = false;
        btn.innerHTML = `<span>💳</span><span>Try Again</span>`;
    }
}

// Display completion
function displayCompletion(data) {
    const completionHTML = `
        <div class="success-box" style="margin-top: 2rem;">
            <div class="success-icon">🎉</div>
            <h2>Claim Resolved!</h2>
            <p style="font-size: 1.125rem; color: var(--text-secondary); margin: 1rem 0 2rem 0;">
                From emergency to resolution in under 5 minutes
            </p>
            
            <div style="background: white; border-radius: var(--radius-lg); padding: 2rem; text-align: left; max-width: 500px; margin: 0 auto;">
                <div style="display: grid; gap: 1rem;">
                    <div style="display: flex; justify-content: space-between; padding-bottom: 1rem; border-bottom: 1px solid var(--border);">
                        <span style="color: var(--text-secondary);">Contractor</span>
                        <strong>${data.contractor.name}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-bottom: 1rem; border-bottom: 1px solid var(--border);">
                        <span style="color: var(--text-secondary);">Arrival Time</span>
                        <strong>${data.contractor.eta}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-bottom: 1rem; border-bottom: 1px solid var(--border);">
                        <span style="color: var(--text-secondary);">Deposit Paid</span>
                        <strong style="color: var(--success);">$${data.payment.deposit.toLocaleString()}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-bottom: 1rem; border-bottom: 1px solid var(--border);">
                        <span style="color: var(--text-secondary);">Remaining Balance</span>
                        <strong>$${data.payment.remaining.toLocaleString()}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary);">Total Cost</span>
                        <strong style="font-size: 1.25rem;">$${data.payment.total_cost.toLocaleString()}</strong>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(74,144,226,0.1); border-radius: var(--radius-md);">
                <p style="margin: 0; color: var(--text-primary);">
                    ✅ <strong>SMS confirmation sent to your phone</strong><br>
                    <span style="font-size: 0.875rem; color: var(--text-secondary);">
                        You'll receive updates as the contractor arrives
                    </span>
                </p>
            </div>
            
            <a href="index.html" class="btn btn-primary" style="margin-top: 2rem; text-decoration: none;">
                <span>← Back to Dashboard</span>
            </a>
        </div>
    `;
    
    analysisResult.insertAdjacentHTML('beforeend', completionHTML);
    
    // Hide contractors
    document.querySelectorAll('.contractor-card').forEach(card => {
        card.style.display = 'none';
    });
    
    // Scroll to completion
    setTimeout(() => {
        document.querySelector('.success-box').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
    }, 100);
    
    // Confetti effect (optional)
    createConfetti();
}

// Simple confetti effect
function createConfetti() {
    const colors = ['#4A90E2', '#6C5CE7', '#48BB78', '#F59E0B'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                top: -10px;
                left: ${Math.random() * 100}vw;
                opacity: 0.8;
                border-radius: 50%;
                pointer-events: none;
                z-index: 10000;
                animation: confettiFall ${2 + Math.random() * 2}s linear forwards;
            `;
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 4000);
        }, i * 30);
    }
}

// Add confetti animation
const confettiStyle = document.createElement('style');
confettiStyle.textContent = `
    @keyframes confettiFall {
        to {
            transform: translateY(100vh) rotate(${Math.random() * 360}deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(confettiStyle);