import random
from datetime import datetime, timedelta
import uuid

class DemoDataGenerator:
    """
    Generate realistic demo data for hackathon presentations.
    Shows the system handling multiple claims simultaneously.
    """
    
    def __init__(self):
        self.demo_scenarios = [
            {
                'message': 'My roof just collapsed after the storm! Water is pouring into my bedroom and I have no idea what to do!',
                'severity': 'critical',
                'damage_type': 'roof',
                'estimated_cost': 8500,
                'contractor': 'Dave\'s Roofing',
                'eta': '45 minutes'
            },
            {
                'message': 'There\'s a massive leak under my kitchen sink. Water everywhere and it won\'t stop!',
                'severity': 'severe',
                'damage_type': 'plumbing',
                'estimated_cost': 1200,
                'contractor': '24/7 Plumbing',
                'eta': '30 minutes'
            },
            {
                'message': 'Lightning struck our house and now half the electrical system is out. Smells like burning.',
                'severity': 'critical',
                'damage_type': 'electrical',
                'estimated_cost': 5500,
                'contractor': 'Spark Electrical',
                'eta': '1 hour'
            },
            {
                'message': 'The storm damaged our fence and broke a window. Glass shattered everywhere.',
                'severity': 'moderate',
                'damage_type': 'storm',
                'estimated_cost': 2800,
                'contractor': 'Storm Repair Co',
                'eta': '2 hours'
            },
            {
                'message': 'Flood water came up through the floorboards. Living room is soaked.',
                'severity': 'severe',
                'damage_type': 'flood',
                'estimated_cost': 12000,
                'contractor': 'Emergency Builders',
                'eta': '1 hour'
            }
        ]
    
    def generate_demo_claim(self, scenario_index=None):
        """Generate a complete demo claim"""
        
        if scenario_index is None:
            scenario = random.choice(self.demo_scenarios)
        else:
            scenario = self.demo_scenarios[scenario_index % len(self.demo_scenarios)]
        
        claim_id = str(uuid.uuid4())[:8]
        
        # Random timestamp in last 24 hours
        hours_ago = random.randint(1, 24)
        timestamp = datetime.now() - timedelta(hours=hours_ago)
        
        # Random completion time (3-7 minutes after start)
        completion_minutes = random.randint(3, 7)
        completion_time = timestamp + timedelta(minutes=completion_minutes)
        
        claim = {
            'id': claim_id,
            'phone': '+61400000000',
            'initial_message': scenario['message'],
            'triage': {
                'response': self._generate_empathy_response(scenario['damage_type']),
                'damage_type': scenario['damage_type'],
                'severity': scenario['severity'],
                'safety_concern': scenario['severity'] in ['critical', 'severe'],
                'location': 'Melbourne, VIC',
                'thinking': f"Assessed as {scenario['severity']} based on immediate safety risk and damage extent"
            },
            'assessment': {
                'description': self._generate_damage_description(scenario['damage_type']),
                'estimated_cost': scenario['estimated_cost'],
                'cost_range': {
                    'min': int(scenario['estimated_cost'] * 0.8),
                    'max': int(scenario['estimated_cost'] * 1.2)
                },
                'urgency': 'immediate' if scenario['severity'] == 'critical' else 'urgent',
                'required_trade': scenario['damage_type'],
                'safety_hazards': self._generate_safety_hazards(scenario['damage_type']),
                'recommended_action': 'Emergency professional repair required immediately'
            },
            'negotiation': {
                'contractors': self._generate_contractors(scenario['estimated_cost']),
                'total_contacted': 3
            },
            'contractor': {
                'name': scenario['contractor'],
                'final_price': scenario['estimated_cost'] * 0.85,
                'eta': scenario['eta'],
                'rating': round(random.uniform(4.5, 5.0), 1)
            },
            'payment': {
                'deposit': scenario['estimated_cost'] * 0.85 * 0.2,
                'total_cost': scenario['estimated_cost'] * 0.85,
                'remaining': scenario['estimated_cost'] * 0.85 * 0.8,
                'payment_id': f"demo_{claim_id}",
                'status': 'completed'
            },
            'status': 'completed',
            'timestamp': timestamp.isoformat(),
            'completion_time': completion_time.isoformat(),
            'steps': [
                'Empathy Agent: Call received and triaged',
                'Visual Agent: AI vision analysis complete',
                f'Haggler Agent: 3 contractors negotiated',
                'Finance Agent: Payment processed, SMS sent'
            ],
            'workflow_state': 'completed',
            'demo': True
        }
        
        claim['negotiation']['best_deal'] = claim['contractor']
        claim['negotiation']['negotiation_summary'] = (
            f"Contacted 3 contractors. Best deal: {scenario['contractor']} "
            f"at ${claim['contractor']['final_price']:.0f}"
        )
        
        return claim
    
    def _generate_empathy_response(self, damage_type):
        responses = {
            'roof': "I understand how stressful this is, especially with water coming in. We're going to get someone to you right away to stop the damage and make your home safe again.",
            'plumbing': "That sounds really overwhelming. Don't worry, we'll have a qualified plumber there very soon to fix this and prevent any further damage.",
            'electrical': "Your safety is our priority. This is serious, and we're dispatching an emergency electrician immediately. Please stay away from any affected areas.",
            'storm': "I know storms can be frightening and the damage can feel overwhelming. We'll get this sorted out quickly and make your home secure again.",
            'flood': "Flood damage is incredibly stressful. We're treating this as urgent and will have a team there as soon as possible to assess and begin repairs."
        }
        return responses.get(damage_type, "We're here to help. Let's get this resolved quickly.")
    
    def _generate_damage_description(self, damage_type):
        descriptions = {
            'roof': "Significant roof structural damage visible with active water intrusion. Multiple shingles displaced, potential beam damage. Immediate tarping required.",
            'plumbing': "Major plumbing leak from supply line. Active water flow causing secondary water damage. Requires immediate shutoff and pipe replacement.",
            'electrical': "Critical electrical damage with signs of arcing. Multiple circuits affected, potential fire hazard. Immediate power isolation required.",
            'storm': "Storm impact damage including broken window and fence structural failure. Debris present, requires cleanup and repair.",
            'flood': "Extensive flood water damage affecting flooring and lower walls. Standing water present, requires immediate extraction and drying."
        }
        return descriptions.get(damage_type, "Property damage requiring professional assessment and repair.")
    
    def _generate_safety_hazards(self, damage_type):
        hazards = {
            'roof': ["Structural instability", "Active water intrusion", "Potential ceiling collapse"],
            'plumbing': ["Water damage", "Potential mold growth", "Slip hazard"],
            'electrical': ["Fire hazard", "Electrocution risk", "Power instability"],
            'storm': ["Sharp glass fragments", "Structural instability", "Weather exposure"],
            'flood': ["Contaminated water", "Electrical hazard", "Structural damage"]
        }
        return hazards.get(damage_type, [])
    
    def _generate_contractors(self, base_cost):
        contractors = []
        for i in range(3):
            price_variation = random.uniform(0.85, 1.15)
            contractors.append({
                'name': f"Contractor {i+1}",
                'final_price': base_cost * price_variation,
                'original_price': base_cost * price_variation * 1.15,
                'discount_percent': 15,
                'eta': ['45 minutes', '1 hour', '2 hours'][i],
                'rating': round(random.uniform(4.3, 4.9), 1),
                'speed': ['fast', 'medium', 'medium'][i]
            })
        return sorted(contractors, key=lambda x: x['final_price'])
    
    def generate_batch_demo_claims(self, count=5):
        """Generate multiple demo claims for dashboard"""
        return [self.generate_demo_claim(i) for i in range(count)]


# Demo mode endpoint decorator
def demo_mode_enabled():
    """Check if demo mode is enabled"""
    import os
    return os.getenv('DEMO_MODE', 'false').lower() == 'true'