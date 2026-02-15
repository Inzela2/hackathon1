
"""
Empathy Agent - GEMINI FLASH POWERED (100% FREE!)

Handles initial emergency triage with empathy and intelligence.
"""

import google.generativeai as genai
import os
import json
import logging

logger = logging.getLogger(__name__)

class EmpathyAgent:
    """Handles initial call triage with empathy - GEMINI FLASH (FREE!)"""
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("💙 Empathy Agent initialized with Gemini Flash (FREE!)")
        
    def triage(self, user_message):
        """Analyze emergency using Gemini Flash"""
        
        prompt = f"""You are an empathetic emergency claims agent for an Australian insurance company. A distressed person just called about property damage.

Their message: "{user_message}"

Your tasks:
1. Provide an empathetic, calming response (2-3 sentences maximum)
2. Extract key information about the damage
3. Assess severity level accurately
4. Identify any safety concerns
5. Extract location if mentioned

Response format (JSON only, no markdown, no explanation):
{{
    "response": "Brief empathetic message here (2-3 sentences)",
    "damage_type": "roof|flood|fire|storm|electrical|water|plumbing|other",
    "severity": "minor|moderate|severe|critical",
    "safety_concern": true/false,
    "location": "extracted location or unknown",
    "thinking": "One sentence explaining your severity assessment"
}}

Severity assessment criteria:
- critical: Immediate life/safety risk, structural collapse, active fire/flood
- severe: Major structural damage, extensive water damage, electrical hazards
- moderate: Significant damage requiring urgent repair, no immediate danger
- minor: Cosmetic or small damage, can wait for standard scheduling

Guidelines:
- Be warm, reassuring, and professional
- Keep response brief but caring (Australian English)
- Assess severity conservatively (better safe than sorry)
- Mark safety_concern as true if ANY risk present"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            
            result = json.loads(response.text)
            
            # Validate required fields
            required_fields = ['response', 'damage_type', 'severity', 'safety_concern', 'location', 'thinking']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing field '{field}' in response, using default")
                    result[field] = self._get_default_value(field)
            
            logger.info(f"✓ Triage complete: {result['severity']} {result['damage_type']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return self._generate_fallback_response()
            
        except Exception as e:
            logger.error(f"Empathy Agent error: {e}")
            return self._generate_fallback_response()
    
    def _get_default_value(self, field):
        """Get default value for missing field"""
        defaults = {
            'response': "I understand this is very stressful. We're here to help you immediately.",
            'damage_type': 'other',
            'severity': 'moderate',
            'safety_concern': True,
            'location': 'unknown',
            'thinking': 'Unable to fully assess, using safe defaults'
        }
        return defaults.get(field, '')
    
    def _generate_fallback_response(self):
        """Generate safe fallback response when AI fails"""
        return {
            "response": "I understand this is very stressful. We're here to help you immediately. Can you tell me more about what happened?",
            "damage_type": "other",
            "severity": "moderate",
            "safety_concern": True,
            "location": "unknown",
            "thinking": "Error in assessment, defaulting to safe moderate severity"
        }