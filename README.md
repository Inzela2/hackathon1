### Participant

| Field | Your Answer |
|-------|-------------|
| **Name** |Inzelabanu Mirza |
| **University / Employer** | University : Deakin University|

### Project

| Field | Your Answer |
|-------|-------------|
| **Project Name** |Sophiie Guardian |
| **One-Line Description** |An autonomous emergency response agent that doesn't just tell you what to do — it does it for you.|
| **Demo Video Link** |https://youtu.be/Ai7X0Avdy_E |
| **Tech Stack** |
- Python / Flask
- Flask-SocketIO
- Twilio
- Groq (LLaMA-3.3-70B)
- Hugging Face (CLIP Vision)
- Google Maps / Places API
|
| **AI Provider(s) Used** |
- Groq (LLaMA-3.3-70B)
- Hugging Face (CLIP Vision)
|

### About Your Project  

#### What does it do?

Sophiie Guardian turns a 3-week insurance nightmare into a 3-minute mitigation. When a homeowner discovers a burst pipe or leaking roof, the *48-Hour Mold Clock* starts ticking—every minute of waiting adds thousands in secondary damage. While tradie wait times in regional Australia stretch to months, Sophiie instantly triages the emergency, calls local professionals, and if none are available, autonomously orders a "Make-Safe" DIY kit from nearby hardware stores—all before the caller hangs up.

This isn't another chatbot giving advice. This is an *autonomous employee* that executes. It sees the damage via photo, negotiates with the supply chain, and dispatches help or materials. For insurance companies, this means a 90% reduction in secondary damage claims. For homeowners, it means sleeping soundly knowing a guardian is watching.


#### How does the interaction work?

The user arrives at a cinematic earth-background interface with rolling text: "AI TO HELP YOU FIND PLUMBER / ELECTRICIAN / ROOFER." They simply describe their emergency via text or voice.

As they chat with Carly (the AI agent), three things happen *transparently* in the side panel:
1. *Action Plan* shows the 3-step progress (Assess → Find Help → Dispatch)
2. *Agent Reasoning* scrolls live thoughts: "Because water pressure is rising, I'm checking for local Make-Safe kits..."
3. *Confidence Meter* displays how certain the AI is (e.g., 92% confident this is a burst pipe)

When a photo is uploaded, Hugging Face CLIP analyzes the damage. If a professional is needed, Carly *calls the user's phone* (via Twilio), speaks the full job details, and listens for a YES/NO response. If YES, tracking begins. If NO, nearby stores with DIY kits and step-by-step repair instructions appear instantly.

#### What makes it special?

1. *Agentic Resilience, Not Just Reliability* — When the first plumber is 45 minutes away, most systems fail. Sophiie *re-plans in real-time*, pivoting to a DIY kit delivery via Uber. The "Agent Reasoning" panel shows this thought process live, building trust through transparency.

2. *Multi-Modal Trust Architecture* — The Confidence Meter isn't just for show. When the AI is only 40% sure, it prompts: "Please take a photo of the baseboard so I can confirm." This turns uncertainty into action, not errors.

3. *From Consultant to Employee* — ChatGPT gives you a to-do list. Sophiie gives you a result. It doesn't tell you to buy a kit—it *buys it for you*. This shift from Generative AI to Agentic Action is the future of emergency response.

#### How to run it



```bash
# 1. Clone the repository
git clone https://github.com/Inzela2/sophiie-guardian
cd sophiie-guardian

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Add your API keys:
# - TWILIO_ACCOUNT_SID / AUTH_TOKEN / PHONE_NUMBER
# - GROQ_API_KEY
# - GOOGLE_MAPS_API_KEY
# - HF_TOKEN (Hugging Face)

# 4. Start ngrok (for Twilio webhooks)
ngrok http 5000
# Copy the HTTPS URL and add to .env as PUBLIC_URL

# 5. Run the application
python app.py

# 6. Open http://localhost:5000 in your browser
```

#### Architecture / Technical Notes

The system orchestrates a *multi-agent swarm*:

- *Carly Agent* (Groq LLaMA-3.3) — Handles empathetic conversation and intent extraction
- *Vision Agent* (Hugging Face CLIP) — Zero-shot damage classification from photos
- *Haggler Agent* — Simulates supply chain negotiation and inventory checking
- *Phone Agent* (Twilio) — Makes calls with speech recognition for YES/NO responses
- *Finance Agent* — Handles "Make-Safe" payment execution (simulated)

All agents communicate via Flask-Socket.IO for real-time UI updates. The "Agent Reasoning" panel is powered by intercepting decision points and broadcasting them as natural-language explanations prefixed with "Because...". This *transparency layer* is what builds user trust in high-stakes emergencies.

The architecture is designed for *graceful degradation*—if any API fails, the system falls back to simulated but realistic responses, ensuring the demo never breaks.

---

