const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '';

const voiceButton = document.getElementById('voiceButton');
const voiceStatus = document.getElementById('voiceStatus');
const voiceTranscript = document.getElementById('voiceTranscript');
const transcriptText = document.getElementById('transcriptText');
const voiceResponse = document.getElementById('voiceResponse');

let isListening = false;
let recognition = null;
let mediaRecorder = null;
let audioChunks = [];

// Check for browser support
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-AU'; // Australian English
    
    recognition.onstart = () => {
        isListening = true;
        voiceButton.classList.add('listening');
        voiceStatus.textContent = '🎤 Listening... speak now';
        voiceTranscript.style.display = 'block';
        transcriptText.textContent = 'Listening...';
        transcriptText.style.fontStyle = 'italic';
    };
    
    recognition.onresult = (event) => {
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
        
        if (interimTranscript) {
            transcriptText.textContent = interimTranscript;
            transcriptText.style.fontStyle = 'italic';
            transcriptText.style.color = 'var(--text-muted)';
        }
        
        if (finalTranscript) {
            transcriptText.textContent = finalTranscript;
            transcriptText.style.fontStyle = 'normal';
            transcriptText.style.color = 'var(--text-primary)';
            
            // Process the emergency
            processVoiceEmergency(finalTranscript);
        }
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        voiceStatus.textContent = '❌ Error: ' + event.error;
        voiceButton.classList.remove('listening');
        isListening = false;
    };
    
    recognition.onend = () => {
        if (isListening && !transcriptText.textContent.includes('Processing')) {
            voiceStatus.textContent = 'Tap microphone to try again';
        }
        voiceButton.classList.remove('listening');
        isListening = false;
    };
    
} else {
    voiceStatus.textContent = '⚠️ Voice recognition not supported in this browser';
    voiceButton.disabled = true;
}

// Voice button click
voiceButton.addEventListener('click', () => {
    if (!recognition) {
        alert('Voice recognition not supported in this browser. Please use Chrome, Safari, or Edge.');
        return;
    }
    
    if (isListening) {
        recognition.stop();
        isListening = false;
        voiceButton.classList.remove('listening');
        voiceStatus.textContent = 'Tap microphone to start';
    } else {
        recognition.start();
    }
});

// Process voice emergency
async function processVoiceEmergency(message) {
    voiceStatus.textContent = '🤖 Processing your emergency...';
    transcriptText.textContent = `"${message}"`;
    
    try {
        const response = await fetch(`${API_URL}/api/start-claim`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message,
                phone: '+61400000000' // Default for demo
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            voiceStatus.textContent = '✅ Claim processed successfully!';
            displayVoiceResponse(data);
            
            // Speak the response (if supported)
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(data.response);
                utterance.lang = 'en-AU';
                utterance.rate = 0.9;
                utterance.pitch = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        } else {
            throw new Error(data.error || 'Unknown error');
        }
        
    } catch (error) {
        voiceStatus.textContent = '❌ Error processing claim';
        alert('Error: ' + error.message);
    }
}

// Display voice response
function displayVoiceResponse(data) {
    voiceResponse.style.display = 'block';
    voiceResponse.innerHTML = `
        <div style="text-align: left;">
            <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1.5rem;">
                <span style="font-size: 2.5rem;">✓</span>
                <div>
                    <h3 style="margin-bottom: 0.5rem;">Claim #${data.claim_id} Created</h3>
                    <p style="color: var(--text-secondary); margin: 0;">Emergency triage complete</p>
                </div>
            </div>
            
            <div style="background: var(--primary-blue-light); border-radius: var(--radius-md); padding: 1.5rem; margin-bottom: 1rem;">
                <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    <strong>AI Response:</strong>
                </p>
                <p style="font-size: 1.125rem; line-height: 1.6; margin: 0;">
                    "${data.response}"
                </p>
            </div>
            
            <div style="margin-bottom: 1.5rem;">
                <span class="severity-badge severity-${data.severity}">
                    ${data.severity} severity
                </span>
            </div>
            
            <div style="background: rgba(74,144,226,0.05); border-radius: var(--radius-md); padding: 1.5rem;">
                <p style="margin: 0 0 1rem 0;">
                    <strong>Next Step:</strong> Upload a photo of the damage
                </p>
                <a href="upload.html?claim=${data.claim_id}" class="btn btn-primary" style="text-decoration: none;">
                    <span>Continue to Photo Upload</span>
                    <span>→</span>
                </a>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        voiceResponse.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// Keyboard shortcut
document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !isListening) {
        e.preventDefault();
        voiceButton.click();
    }
});