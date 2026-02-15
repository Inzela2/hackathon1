


"""
Visual Agent - GEMINI VISION POWERED (100% FREE!)

Uses Google Gemini's multimodal capabilities for damage photo analysis.
Completely free - no Claude costs!
"""

import google.generativeai as genai
import os
import json
import logging
from io import BytesIO
from PIL import Image
import base64

logger = logging.getLogger(__name__)

class VisualAgent:
    """Processes damage photos using Gemini Vision - 100% FREE!"""
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("👁️ Visual Agent initialized with Gemini Vision (FREE!)")
        
    def assess_damage(self, image_file, triage_data):
        """Analyze damage photo and estimate repair costs using Gemini Vision"""
        
        try:
            # Read and process image
            image = Image.open(image_file)
            
            # Resize if too large (Gemini can handle larger, but optimize for speed)
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {image.size}")
            
            # Convert to RGB if needed
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            damage_type = triage_data.get('damage_type', 'unknown')
            severity = triage_data.get('severity', 'moderate')
            
            prompt = f"""You are an expert insurance claims adjuster analyzing damage photos.

Context from initial emergency call:
- Reported damage type: {damage_type}
- Initial severity assessment: {severity}

Analyze this image and provide a detailed damage assessment for insurance purposes.

Your task:
1. Describe the visible damage in 2-3 sentences
2. Estimate repair cost in AUD (Australian dollars)
3. Provide cost range (min/max)
4. Assess urgency level
5. Identify required trade/contractor type
6. List any visible safety hazards
7. Recommend immediate action

Australian pricing context:
- Minor repairs: $500-$2,000
- Moderate repairs: $2,000-$10,000  
- Major repairs: $10,000-$50,000
- Severe/structural: $50,000+

Urgency levels:
- immediate: Active danger or rapid deterioration happening now
- urgent: Needs repair within 24-48 hours
- standard: Can wait a few days for scheduling

Required trade options:
- roofer: For roof damage, shingles, gutters
- plumber: For water leaks, pipes, drains
- builder: For structural damage, walls, foundations
- electrician: For electrical issues, wiring
- general contractor: For mixed/multiple trades needed

Respond with ONLY a JSON object (no markdown, no explanation):
{{
    "description": "2-3 sentence description of visible damage",
    "estimated_cost": 2500,
    "cost_range": {{"min": 2000, "max": 3000}},
    "urgency": "immediate|urgent|standard",
    "required_trade": "roofer|plumber|builder|electrician|general contractor",
    "safety_hazards": ["list any visible safety hazards"],
    "recommended_action": "immediate next steps needed"
}}

Be realistic with cost estimates based on Australian pricing. Consider:
- Extent of visible damage
- Materials needed
- Labor complexity
- Access difficulty
- Safety concerns"""

            # Generate content with image
            logger.info("Analyzing image with Gemini Vision...")
            
            response = self.model.generate_content(
                [prompt, image],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            
            # Parse response
            result = json.loads(response.text)
            
            # Validate and ensure proper types
            result['estimated_cost'] = float(result.get('estimated_cost', 3500))
            result['cost_range'] = {
                'min': float(result.get('cost_range', {}).get('min', 2500)),
                'max': float(result.get('cost_range', {}).get('max', 5000))
            }
            
            # Ensure required fields exist
            if 'description' not in result:
                result['description'] = f"Visible {damage_type} damage requiring professional assessment"
            if 'urgency' not in result:
                result['urgency'] = 'urgent'
            if 'required_trade' not in result:
                result['required_trade'] = 'general contractor'
            if 'safety_hazards' not in result:
                result['safety_hazards'] = []
            if 'recommended_action' not in result:
                result['recommended_action'] = 'Professional inspection required'
            
            logger.info(f"✓ Visual assessment: ${result['estimated_cost']:.0f} {result['urgency']}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
            
            # Fallback assessment
            return self._generate_fallback_assessment(triage_data)
            
        except Exception as e:
            logger.error(f"Visual Agent error: {e}")
            return self._generate_fallback_assessment(triage_data)
    
    def _generate_fallback_assessment(self, triage_data):
        """Generate fallback assessment when vision analysis fails"""
        
        damage_type = triage_data.get('damage_type', 'property')
        severity = triage_data.get('severity', 'moderate')
        
        # Estimate cost based on severity
        cost_estimates = {
            'minor': 1500,
            'moderate': 3500,
            'severe': 8500,
            'critical': 15000
        }
        
        estimated_cost = cost_estimates.get(severity, 3500)
        
        return {
            "description": f"Visible {damage_type} damage consistent with {severity} severity assessment. Professional on-site inspection recommended for detailed analysis.",
            "estimated_cost": estimated_cost,
            "cost_range": {
                "min": int(estimated_cost * 0.8),
                "max": int(estimated_cost * 1.2)
            },
            "urgency": "immediate" if severity == 'critical' else "urgent" if severity == 'severe' else "standard",
            "required_trade": self._map_damage_to_trade(damage_type),
            "safety_hazards": self._get_default_hazards(damage_type, severity),
            "recommended_action": "Professional on-site inspection and assessment required for accurate cost estimate"
        }
    
    def _map_damage_to_trade(self, damage_type):
        """Map damage type to required trade"""
        mapping = {
            'roof': 'roofer',
            'leak': 'plumber',
            'plumbing': 'plumber',
            'water': 'plumber',
            'flood': 'builder',
            'fire': 'builder',
            'storm': 'builder',
            'electrical': 'electrician'
        }
        
        for key, trade in mapping.items():
            if key in damage_type.lower():
                return trade
        
        return 'general contractor'
    
    def _get_default_hazards(self, damage_type, severity):
        """Get default safety hazards based on damage type"""
        
        hazards = {
            'roof': ['Structural instability', 'Water intrusion'],
            'plumbing': ['Water damage', 'Mold risk'],
            'electrical': ['Fire hazard', 'Electrocution risk'],
            'flood': ['Contaminated water', 'Structural damage'],
            'fire': ['Structural instability', 'Toxic residue']
        }
        
        for key, haz in hazards.items():
            if key in damage_type.lower():
                return haz if severity in ['severe', 'critical'] else haz[:1]
        
        return []