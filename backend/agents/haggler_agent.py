# # import anthropic
# # import os
# # import json
# # import random
# # import logging

# # logger = logging.getLogger(__name__)

# # class HagglerAgent:
# #     """Negotiates with contractors - COST OPTIMIZED with Haiku"""
    
# #     def __init__(self):
# #         api_key = os.getenv('ANTHROPIC_API_KEY')
# #         if not api_key:
# #             raise ValueError("ANTHROPIC_API_KEY not found in environment")
# #         self.client = anthropic.Anthropic(api_key=api_key)
# #         self.load_contractors()
# #         logger.info("💼 Haggler Agent initialized with Haiku model")
        
# #     def load_contractors(self):
# #         """Load mock contractor database"""
# #         contractor_file = os.path.join(
# #             os.path.dirname(__file__), 
# #             '../../mock_data/contractors.json'
# #         )
        
# #         try:
# #             with open(contractor_file, 'r') as f:
# #                 self.contractors_db = json.load(f)
# #                 logger.info(f"✓ Loaded {sum(len(v) for v in self.contractors_db.values())} contractors")
# #         except FileNotFoundError:
# #             logger.warning("Contractor DB not found, using defaults")
# #             self._create_default_contractors()
    
# #     def _create_default_contractors(self):
# #         """Create default contractor database"""
# #         self.contractors_db = {
# #             "roofer": [
# #                 {"name": "Dave's Roofing", "base_rate": 150, "rating": 4.8, "speed": "fast"},
# #                 {"name": "Apex Roof Repairs", "base_rate": 180, "rating": 4.9, "speed": "medium"},
# #                 {"name": "QuickFix Roofing", "base_rate": 120, "rating": 4.5, "speed": "fast"}
# #             ],
# #             "plumber": [
# #                 {"name": "24/7 Plumbing", "base_rate": 130, "rating": 4.7, "speed": "fast"},
# #                 {"name": "Pro Plumbers", "base_rate": 160, "rating": 4.8, "speed": "medium"},
# #                 {"name": "Rapid Response Plumbing", "base_rate": 110, "rating": 4.4, "speed": "fast"}
# #             ],
# #             "builder": [
# #                 {"name": "Storm Repair Co", "base_rate": 200, "rating": 4.9, "speed": "medium"},
# #                 {"name": "Emergency Builders", "base_rate": 220, "rating": 4.7, "speed": "fast"},
# #                 {"name": "Reliable Repairs", "base_rate": 180, "rating": 4.6, "speed": "medium"}
# #             ],
# #             "electrician": [
# #                 {"name": "Spark Electrical", "base_rate": 140, "rating": 4.8, "speed": "fast"},
# #                 {"name": "PowerPro Electric", "base_rate": 160, "rating": 4.9, "speed": "medium"},
# #                 {"name": "Quick Sparks", "base_rate": 110, "rating": 4.4, "speed": "fast"}
# #             ],
# #             "general contractor": [
# #                 {"name": "All-Trade Repairs", "base_rate": 170, "rating": 4.7, "speed": "medium"},
# #                 {"name": "Emergency Services", "base_rate": 190, "rating": 4.8, "speed": "fast"},
# #                 {"name": "General Contractors Plus", "base_rate": 150, "rating": 4.5, "speed": "medium"}
# #             ]
# #         }
    
# #     def negotiate(self, damage_type, severity, estimated_cost):
# #         """Find contractors and negotiate pricing"""
        
# #         # Map damage to trade
# #         trade = self._map_damage_to_trade(damage_type)
# #         logger.info(f"Searching for {trade} contractors...")
        
# #         # Get available contractors
# #         available = self.contractors_db.get(trade, self.contractors_db["general contractor"])
        
# #         # Select top 3
# #         contractors = random.sample(available, min(3, len(available)))
        
# #         # Negotiate with each
# #         results = []
# #         for contractor in contractors:
# #             negotiation = self._negotiate_with_contractor(
# #                 contractor, estimated_cost, severity
# #             )
# #             results.append(negotiation)
        
# #         # Sort by best value
# #         results.sort(key=lambda x: x['final_price'])
        
# #         savings = results[-1]['final_price'] - results[0]['final_price']
        
# #         logger.info(f"✓ Best deal: {results[0]['name']} at ${results[0]['final_price']} (saved ${savings:.0f})")
        
# #         return {
# #             "contractors": results,
# #             "best_deal": results[0],
# #             "total_contacted": len(results),
# #             "negotiation_summary": f"Contacted {len(results)} contractors. Best deal: {results[0]['name']} at ${results[0]['final_price']:.0f} (saved ${savings:.0f} vs highest quote)"
# #         }
    
# #     def _map_damage_to_trade(self, damage_type):
# #         """Map damage type to required trade"""
# #         mapping = {
# #             "roof": "roofer",
# #             "leak": "plumber",
# #             "flood": "builder",
# #             "fire": "builder",
# #             "electrical": "electrician",
# #             "storm": "builder",
# #             "water": "plumber",
# #             "plumbing": "plumber"
# #         }
        
# #         damage_lower = damage_type.lower()
# #         for key, value in mapping.items():
# #             if key in damage_lower:
# #                 return value
        
# #         return "general contractor"
    
# #     def _negotiate_with_contractor(self, contractor, estimated_cost, severity):
# #         """AI-powered negotiation with single contractor using Haiku"""
        
# #         # Calculate base quote
# #         base_quote = contractor['base_rate'] * max(1, estimated_cost / 1000)
        
# #         # Urgency multiplier
# #         urgency_multiplier = {
# #             "critical": 1.4,
# #             "severe": 1.25,
# #             "moderate": 1.1,
# #             "minor": 1.0
# #         }.get(severity, 1.1)
        
# #         initial_quote = base_quote * urgency_multiplier
        
# #         # AI negotiation using Haiku
# #         prompt = f"""You're negotiating an emergency repair with {contractor['name']}.

# # Contractor details:
# # - Initial quote: ${initial_quote:.0f}
# # - Rating: {contractor['rating']}/5
# # - Response speed: {contractor['speed']}

# # Job details:
# # - Urgency: {severity}
# # - Estimated work: ${estimated_cost}

# # Negotiate to get:
# # 1. Lower price (10-20% discount if possible)
# # 2. Fastest arrival time
# # 3. Reasonable deposit

# # Respond with JSON only:
# # {{
# #     "final_price": negotiated total price,
# #     "discount_percent": percentage saved,
# #     "eta": "time like '45 minutes' or '2 hours'",
# #     "deposit_required": deposit amount (typically 20% of final),
# #     "negotiation_notes": "one sentence: how you got the deal"
# # }}

# # Be realistic - high-rated contractors won't give huge discounts, but you can get better ETA or terms."""

# #         try:
# #             message = self.client.messages.create(
# #                 model="claude-haiku-4-20250514",  # Haiku for cost efficiency
# #                 max_tokens=300,
# #                 temperature=0.7,
# #                 messages=[{"role": "user", "content": prompt}]
# #             )
            
# #             response_text = message.content[0].text.strip()
            
# #             if response_text.startswith('```'):
# #                 response_text = response_text.split('```')[1]
# #                 if response_text.startswith('json'):
# #                     response_text = response_text[4:]
# #                 response_text = response_text.strip()
            
# #             result = json.loads(response_text)
            
# #             # Add contractor info
# #             result['name'] = contractor['name']
# #             result['rating'] = contractor['rating']
# #             result['speed'] = contractor['speed']
# #             result['original_price'] = round(initial_quote, 2)
            
# #             return result
            
# #         except Exception as e:
# #             logger.error(f"Negotiation AI error: {e}, using fallback")
            
# #             # Fallback negotiation
# #             discount = random.uniform(0.10, 0.20)
# #             final_price = initial_quote * (1 - discount)
            
# #             return {
# #                 "name": contractor['name'],
# #                 "final_price": round(final_price, 2),
# #                 "original_price": round(initial_quote, 2),
# #                 "discount_percent": round(discount * 100, 1),
# #                 "eta": "45 minutes" if contractor['speed'] == 'fast' else "2 hours",
# #                 "deposit_required": round(final_price * 0.2, 2),
# #                 "rating": contractor['rating'],
# #                 "speed": contractor['speed'],
# #                 "negotiation_notes": f"Secured {round(discount*100)}% emergency discount for quick response"
# #             }





















# import google.generativeai as genai
# import os
# import json
# import random
# import logging

# logger = logging.getLogger(__name__)

# class HagglerAgent:
#     """Negotiates with contractors - COST OPTIMIZED with Haiku"""
    
#     def __init__(self):
#         api_key = os.getenv('GOOGLE_API_KEY')
#         if not api_key:
#             raise ValueError("GOOGLE_API_KEY not found in environment")
        
#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel('gemini-1.5-flash')
#         self.load_contractors()
#         logger.info("💼 Haggler Agent initialized with Gemini model")
        
#     def load_contractors(self):
#         """Load mock contractor database"""
#         contractor_file = os.path.join(
#             os.path.dirname(__file__), 
#             '../../mock_data/contractors.json'
#         )
        
#         try:
#             with open(contractor_file, 'r') as f:
#                 self.contractors_db = json.load(f)
#                 logger.info(f"✓ Loaded {sum(len(v) for v in self.contractors_db.values())} contractors")
#         except FileNotFoundError:
#             logger.warning("Contractor DB not found, using defaults")
#             self._create_default_contractors()
    
#     def _create_default_contractors(self):
#         """Create default contractor database"""
#         self.contractors_db = {
#             "roofer": [
#                 {"name": "Dave's Roofing", "base_rate": 150, "rating": 4.8, "speed": "fast"},
#                 {"name": "Apex Roof Repairs", "base_rate": 180, "rating": 4.9, "speed": "medium"},
#                 {"name": "QuickFix Roofing", "base_rate": 120, "rating": 4.5, "speed": "fast"}
#             ],
#             "plumber": [
#                 {"name": "24/7 Plumbing", "base_rate": 130, "rating": 4.7, "speed": "fast"},
#                 {"name": "Pro Plumbers", "base_rate": 160, "rating": 4.8, "speed": "medium"},
#                 {"name": "Rapid Response Plumbing", "base_rate": 110, "rating": 4.4, "speed": "fast"}
#             ],
#             "builder": [
#                 {"name": "Storm Repair Co", "base_rate": 200, "rating": 4.9, "speed": "medium"},
#                 {"name": "Emergency Builders", "base_rate": 220, "rating": 4.7, "speed": "fast"},
#                 {"name": "Reliable Repairs", "base_rate": 180, "rating": 4.6, "speed": "medium"}
#             ],
#             "electrician": [
#                 {"name": "Spark Electrical", "base_rate": 140, "rating": 4.8, "speed": "fast"},
#                 {"name": "PowerPro Electric", "base_rate": 160, "rating": 4.9, "speed": "medium"},
#                 {"name": "Quick Sparks", "base_rate": 110, "rating": 4.4, "speed": "fast"}
#             ],
#             "general contractor": [
#                 {"name": "All-Trade Repairs", "base_rate": 170, "rating": 4.7, "speed": "medium"},
#                 {"name": "Emergency Services", "base_rate": 190, "rating": 4.8, "speed": "fast"},
#                 {"name": "General Contractors Plus", "base_rate": 150, "rating": 4.5, "speed": "medium"}
#             ]
#         }
    
#     def negotiate(self, damage_type, severity, estimated_cost):
#         """Find contractors and negotiate pricing"""
        
#         # Map damage to trade
#         trade = self._map_damage_to_trade(damage_type)
#         logger.info(f"Searching for {trade} contractors...")
        
#         # Get available contractors
#         available = self.contractors_db.get(trade, self.contractors_db["general contractor"])
        
#         # Select top 3
#         contractors = random.sample(available, min(3, len(available)))
        
#         # Negotiate with each
#         results = []
#         for contractor in contractors:
#             negotiation = self._negotiate_with_contractor(
#                 contractor, estimated_cost, severity
#             )
#             results.append(negotiation)
        
#         # Sort by best value
#         results.sort(key=lambda x: x['final_price'])
        
#         savings = results[-1]['final_price'] - results[0]['final_price']
        
#         logger.info(f"✓ Best deal: {results[0]['name']} at ${results[0]['final_price']} (saved ${savings:.0f})")
        
#         return {
#             "contractors": results,
#             "best_deal": results[0],
#             "total_contacted": len(results),
#             "negotiation_summary": f"Contacted {len(results)} contractors. Best deal: {results[0]['name']} at ${results[0]['final_price']:.0f} (saved ${savings:.0f} vs highest quote)"
#         }
    
#     def _map_damage_to_trade(self, damage_type):
#         """Map damage type to required trade"""
#         mapping = {
#             "roof": "roofer",
#             "leak": "plumber",
#             "flood": "builder",
#             "fire": "builder",
#             "electrical": "electrician",
#             "storm": "builder",
#             "water": "plumber",
#             "plumbing": "plumber"
#         }
        
#         damage_lower = damage_type.lower()
#         for key, value in mapping.items():
#             if key in damage_lower:
#                 return value
        
#         return "general contractor"
    
#     def _negotiate_with_contractor(self, contractor, estimated_cost, severity):
#         """AI-powered negotiation with single contractor using Gemini"""
        
#         # Calculate base quote
#         base_quote = contractor['base_rate'] * max(1, estimated_cost / 1000)
        
#         # Urgency multiplier
#         urgency_multiplier = {
#             "critical": 1.4,
#             "severe": 1.25,
#             "moderate": 1.1,
#             "minor": 1.0
#         }.get(severity, 1.1)
        
#         initial_quote = base_quote * urgency_multiplier
        
#         # AI negotiation using Gemini
#         prompt = f"""You're negotiating an emergency repair with {contractor['name']}.

# Contractor details:
# - Initial quote: ${initial_quote:.0f}
# - Rating: {contractor['rating']}/5
# - Response speed: {contractor['speed']}

# Job details:
# - Urgency: {severity}
# - Estimated work: ${estimated_cost}

# Negotiate to get:
# 1. Lower price (10-20% discount if possible)
# 2. Fastest arrival time
# 3. Reasonable deposit

# Respond with JSON only:
# {{
#     "final_price": negotiated total price,
#     "discount_percent": percentage saved,
#     "eta": "time like '45 minutes' or '2 hours'",
#     "deposit_required": deposit amount (typically 20% of final),
#     "negotiation_notes": "one sentence: how you got the deal"
# }}

# Be realistic - high-rated contractors won't give huge discounts, but you can get better ETA or terms."""

#         try:
#             response = self.model.generate_content(
#                 prompt,
#                 generation_config=genai.GenerationConfig(
#                     response_mime_type="application/json"
#                 )
#             )
            
#             result = json.loads(response.text)
            
#             # Add contractor info
#             result['name'] = contractor['name']
#             result['rating'] = contractor['rating']
#             result['speed'] = contractor['speed']
#             result['original_price'] = round(initial_quote, 2)
            
#             return result
            
#         except Exception as e:
#             logger.error(f"Negotiation AI error: {e}, using fallback")
            
#             # Fallback negotiation
#             discount = random.uniform(0.10, 0.20)
#             final_price = initial_quote * (1 - discount)
            
#             return {
#                 "name": contractor['name'],
#                 "final_price": round(final_price, 2),
#                 "original_price": round(initial_quote, 2),
#                 "discount_percent": round(discount * 100, 1),
#                 "eta": "45 minutes" if contractor['speed'] == 'fast' else "2 hours",
#                 "deposit_required": round(final_price * 0.2, 2),
#                 "rating": contractor['rating'],
#                 "speed": contractor['speed'],
#                 "negotiation_notes": f"Secured {round(discount*100)}% emergency discount for quick response"
#             }







































# """
# Haggler Agent - GROQ POWERED (100% FREE & SUPER FAST!)

# Uses Groq's lightning-fast Llama 3.1 70B for contractor negotiations.
# """

# from groq import Groq
# import os
# import json
# import random
# import logging

# logger = logging.getLogger(__name__)

# class HagglerAgent:
#     """Negotiates with contractors - GROQ POWERED (FREE & BLAZING FAST!)"""
    
#     def __init__(self):
#         api_key = os.getenv('GROQ_API_KEY')
#         if not api_key:
#             raise ValueError("GROQ_API_KEY not found in environment")
        
#         self.client = Groq(api_key=api_key)
#         self.load_contractors()
#         logger.info("💼 Haggler Agent initialized with Groq Llama 3.1 70B (FREE!)")
        
#     def load_contractors(self):
#         """Load mock contractor database"""
#         contractor_file = os.path.join(
#             os.path.dirname(__file__), 
#             '../../mock_data/contractors.json'
#         )
        
#         try:
#             with open(contractor_file, 'r') as f:
#                 self.contractors_db = json.load(f)
#                 logger.info(f"✓ Loaded {sum(len(v) for v in self.contractors_db.values())} contractors")
#         except FileNotFoundError:
#             logger.warning("Contractor DB not found, using defaults")
#             self._create_default_contractors()
    
#     def _create_default_contractors(self):
#         """Create default contractor database"""
#         self.contractors_db = {
#             "roofer": [
#                 {"name": "Dave's Roofing", "base_rate": 150, "rating": 4.8, "speed": "fast"},
#                 {"name": "Apex Roof Repairs", "base_rate": 180, "rating": 4.9, "speed": "medium"},
#                 {"name": "QuickFix Roofing", "base_rate": 120, "rating": 4.5, "speed": "fast"}
#             ],
#             "plumber": [
#                 {"name": "24/7 Plumbing", "base_rate": 130, "rating": 4.7, "speed": "fast"},
#                 {"name": "Pro Plumbers", "base_rate": 160, "rating": 4.8, "speed": "medium"},
#                 {"name": "Rapid Response Plumbing", "base_rate": 110, "rating": 4.4, "speed": "fast"}
#             ],
#             "builder": [
#                 {"name": "Storm Repair Co", "base_rate": 200, "rating": 4.9, "speed": "medium"},
#                 {"name": "Emergency Builders", "base_rate": 220, "rating": 4.7, "speed": "fast"},
#                 {"name": "Reliable Repairs", "base_rate": 180, "rating": 4.6, "speed": "medium"}
#             ],
#             "electrician": [
#                 {"name": "Spark Electrical", "base_rate": 140, "rating": 4.8, "speed": "fast"},
#                 {"name": "PowerPro Electric", "base_rate": 160, "rating": 4.9, "speed": "medium"},
#                 {"name": "Quick Sparks", "base_rate": 110, "rating": 4.4, "speed": "fast"}
#             ],
#             "general contractor": [
#                 {"name": "All-Trade Repairs", "base_rate": 170, "rating": 4.7, "speed": "medium"},
#                 {"name": "Emergency Services", "base_rate": 190, "rating": 4.8, "speed": "fast"},
#                 {"name": "General Contractors Plus", "base_rate": 150, "rating": 4.5, "speed": "medium"}
#             ]
#         }
    
#     def negotiate(self, damage_type, severity, estimated_cost):
#         """Find contractors and negotiate pricing"""
        
#         # Map damage to trade
#         trade = self._map_damage_to_trade(damage_type)
#         logger.info(f"Searching for {trade} contractors...")
        
#         # Get available contractors
#         available = self.contractors_db.get(trade, self.contractors_db["general contractor"])
        
#         # Select top 3
#         contractors = random.sample(available, min(3, len(available)))
        
#         # Negotiate with each
#         results = []
#         for contractor in contractors:
#             negotiation = self._negotiate_with_contractor(
#                 contractor, estimated_cost, severity
#             )
#             results.append(negotiation)
        
#         # Sort by best value
#         results.sort(key=lambda x: x['final_price'])
        
#         savings = results[-1]['final_price'] - results[0]['final_price']
        
#         logger.info(f"✓ Best deal: {results[0]['name']} at ${results[0]['final_price']:.0f} (saved ${savings:.0f})")
        
#         return {
#             "contractors": results,
#             "best_deal": results[0],
#             "total_contacted": len(results),
#             "negotiation_summary": f"Contacted {len(results)} contractors. Best deal: {results[0]['name']} at ${results[0]['final_price']:.0f} (saved ${savings:.0f} vs highest quote)"
#         }
    
#     def _map_damage_to_trade(self, damage_type):
#         """Map damage type to required trade"""
#         mapping = {
#             "roof": "roofer",
#             "leak": "plumber",
#             "flood": "builder",
#             "fire": "builder",
#             "electrical": "electrician",
#             "storm": "builder",
#             "water": "plumber",
#             "plumbing": "plumber"
#         }
        
#         damage_lower = damage_type.lower()
#         for key, value in mapping.items():
#             if key in damage_lower:
#                 return value
        
#         return "general contractor"
    
#     def _negotiate_with_contractor(self, contractor, estimated_cost, severity):
#         """AI-powered negotiation using Groq (SUPER FAST!)"""
        
#         # Calculate base quote
#         base_quote = contractor['base_rate'] * max(1, estimated_cost / 1000)
        
#         # Urgency multiplier
#         urgency_multiplier = {
#             "critical": 1.4,
#             "severe": 1.25,
#             "moderate": 1.1,
#             "minor": 1.0
#         }.get(severity, 1.1)
        
#         initial_quote = base_quote * urgency_multiplier
        
#         prompt = f"""You're negotiating an emergency repair with {contractor['name']}.

# Contractor details:
# - Initial quote: ${initial_quote:.0f}
# - Rating: {contractor['rating']}/5
# - Response speed: {contractor['speed']}

# Job details:
# - Urgency: {severity}
# - Estimated work: ${estimated_cost}

# Negotiate to get:
# 1. Lower price (aim for 10-20% discount)
# 2. Fastest arrival time
# 3. Reasonable deposit

# Respond with ONLY a JSON object (no markdown, no explanation):
# {{
#     "final_price": negotiated total price as number,
#     "discount_percent": percentage saved as number,
#     "eta": "time like '45 minutes' or '2 hours'",
#     "deposit_required": deposit amount as number (typically 20% of final),
#     "negotiation_notes": "one sentence: how you got the deal"
# }}

# Be realistic - high-rated contractors won't give huge discounts."""

#         try:
#             chat_completion = self.client.chat.completions.create(
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are an expert negotiator. Always respond with valid JSON only."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 model="llama-3.1-70b-versatile",
#                 temperature=0.7,
#                 max_tokens=300,
#                 response_format={"type": "json_object"}
#             )
            
#             response_text = chat_completion.choices[0].message.content.strip()
#             result = json.loads(response_text)
            
#             # Add contractor info and ensure types
#             result['name'] = contractor['name']
#             result['rating'] = contractor['rating']
#             result['speed'] = contractor['speed']
#             result['original_price'] = round(initial_quote, 2)
#             result['final_price'] = float(result['final_price'])
#             result['discount_percent'] = float(result['discount_percent'])
#             result['deposit_required'] = float(result['deposit_required'])
            
#             return result
            
#         except Exception as e:
#             logger.error(f"Groq error: {e}, using fallback")
            
#             # Fallback
#             discount = random.uniform(0.10, 0.20)
#             final_price = initial_quote * (1 - discount)
            
#             return {
#                 "name": contractor['name'],
#                 "final_price": round(final_price, 2),
#                 "original_price": round(initial_quote, 2),
#                 "discount_percent": round(discount * 100, 1),
#                 "eta": "45 minutes" if contractor['speed'] == 'fast' else "2 hours",
#                 "deposit_required": round(final_price * 0.2, 2),
#                 "rating": contractor['rating'],
#                 "speed": contractor['speed'],
#                 "negotiation_notes": f"Secured {round(discount*100)}% emergency discount"
#             }






















"""
Haggler Agent - GROQ POWERED (100% FREE & SUPER FAST!)

Uses Groq's lightning-fast Llama 3.1 70B for contractor negotiations.
"""

from groq import Groq
import os
import json
import random
import logging

logger = logging.getLogger(__name__)

class HagglerAgent:
    """Negotiates with contractors - GROQ POWERED (FREE & BLAZING FAST!)"""
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=api_key)
        self.load_contractors()
        logger.info("💼 Haggler Agent initialized with Groq Llama 3.1 70B (FREE!)")
        
    def load_contractors(self):
        """Load mock contractor database"""
        contractor_file = os.path.join(
            os.path.dirname(__file__), 
            '../../mock_data/contractors.json'
        )
        
        try:
            with open(contractor_file, 'r') as f:
                self.contractors_db = json.load(f)
                logger.info(f"✓ Loaded {sum(len(v) for v in self.contractors_db.values())} contractors")
        except FileNotFoundError:
            logger.warning("Contractor DB not found, using defaults")
            self._create_default_contractors()
    
    def _create_default_contractors(self):
        """Create default contractor database"""
        self.contractors_db = {
            "roofer": [
                {"name": "Dave's Roofing", "base_rate": 150, "rating": 4.8, "speed": "fast"},
                {"name": "Apex Roof Repairs", "base_rate": 180, "rating": 4.9, "speed": "medium"},
                {"name": "QuickFix Roofing", "base_rate": 120, "rating": 4.5, "speed": "fast"}
            ],
            "plumber": [
                {"name": "24/7 Plumbing", "base_rate": 130, "rating": 4.7, "speed": "fast"},
                {"name": "Pro Plumbers", "base_rate": 160, "rating": 4.8, "speed": "medium"},
                {"name": "Rapid Response Plumbing", "base_rate": 110, "rating": 4.4, "speed": "fast"}
            ],
            "builder": [
                {"name": "Storm Repair Co", "base_rate": 200, "rating": 4.9, "speed": "medium"},
                {"name": "Emergency Builders", "base_rate": 220, "rating": 4.7, "speed": "fast"},
                {"name": "Reliable Repairs", "base_rate": 180, "rating": 4.6, "speed": "medium"}
            ],
            "electrician": [
                {"name": "Spark Electrical", "base_rate": 140, "rating": 4.8, "speed": "fast"},
                {"name": "PowerPro Electric", "base_rate": 160, "rating": 4.9, "speed": "medium"},
                {"name": "Quick Sparks", "base_rate": 110, "rating": 4.4, "speed": "fast"}
            ],
            "general contractor": [
                {"name": "All-Trade Repairs", "base_rate": 170, "rating": 4.7, "speed": "medium"},
                {"name": "Emergency Services", "base_rate": 190, "rating": 4.8, "speed": "fast"},
                {"name": "General Contractors Plus", "base_rate": 150, "rating": 4.5, "speed": "medium"}
            ]
        }
    
    def negotiate(self, damage_type, severity, estimated_cost):
        """Find contractors and negotiate pricing"""
        
        # Map damage to trade
        trade = self._map_damage_to_trade(damage_type)
        logger.info(f"Searching for {trade} contractors...")
        
        # Get available contractors - WITH FALLBACK!
        available = self.contractors_db.get(trade)
        
        # FIX: If trade not found, use general contractor
        if not available:
            logger.warning(f"Trade '{trade}' not found, using general contractor")
            available = self.contractors_db.get("general contractor", [])
        
        # FIX: If still empty, create default contractors
        if not available or len(available) == 0:
            logger.error("No contractors found! Using emergency defaults")
            available = [
                {"name": "Emergency Response Services", "base_rate": 180, "rating": 4.7, "speed": "fast"},
                {"name": "24/7 Property Rescue", "base_rate": 190, "rating": 4.6, "speed": "fast"},
                {"name": "Rapid Repair Co", "base_rate": 170, "rating": 4.5, "speed": "medium"}
            ]
        
        # Select top 3
        contractors = random.sample(available, min(3, len(available)))
        
        # Negotiate with each
        results = []
        for contractor in contractors:
            negotiation = self._negotiate_with_contractor(
                contractor, estimated_cost, severity
            )
            results.append(negotiation)
        
        # Sort by best value
        results.sort(key=lambda x: x['final_price'])
        
        savings = results[-1]['final_price'] - results[0]['final_price']
        
        logger.info(f"✓ Best deal: {results[0]['name']} at ${results[0]['final_price']:.0f} (saved ${savings:.0f})")
        
        return {
            "contractors": results,
            "best_deal": results[0],
            "total_contacted": len(results),
            "negotiation_summary": f"Contacted {len(results)} contractors. Best deal: {results[0]['name']} at ${results[0]['final_price']:.0f} (saved ${savings:.0f} vs highest quote)"
        }
    
    def _map_damage_to_trade(self, damage_type):
        """Map damage type to required trade"""
        mapping = {
            "roof": "roofer",
            "leak": "plumber",
            "flood": "builder",
            "fire": "builder",
            "electrical": "electrician",
            "storm": "builder",
            "water": "plumber",
            "plumbing": "plumber"
        }
        
        damage_lower = damage_type.lower()
        for key, value in mapping.items():
            if key in damage_lower:
                return value
        
        return "general contractor"
    
    def _negotiate_with_contractor(self, contractor, estimated_cost, severity):
        """AI-powered negotiation using Groq (SUPER FAST!)"""
        
        # Calculate base quote
        base_quote = contractor['base_rate'] * max(1, estimated_cost / 1000)
        
        # Urgency multiplier
        urgency_multiplier = {
            "critical": 1.4,
            "severe": 1.25,
            "moderate": 1.1,
            "minor": 1.0
        }.get(severity, 1.1)
        
        initial_quote = base_quote * urgency_multiplier
        
        prompt = f"""You're negotiating an emergency repair with {contractor['name']}.

Contractor details:
- Initial quote: ${initial_quote:.0f}
- Rating: {contractor['rating']}/5
- Response speed: {contractor['speed']}

Job details:
- Urgency: {severity}
- Estimated work: ${estimated_cost}

Negotiate to get:
1. Lower price (aim for 10-20% discount)
2. Fastest arrival time
3. Reasonable deposit

Respond with ONLY a JSON object (no markdown, no explanation):
{{
    "final_price": negotiated total price as number,
    "discount_percent": percentage saved as number,
    "eta": "time like '45 minutes' or '2 hours'",
    "deposit_required": deposit amount as number (typically 20% of final),
    "negotiation_notes": "one sentence: how you got the deal"
}}

Be realistic - high-rated contractors won't give huge discounts."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert negotiator. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-70b-versatile",
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            result = json.loads(response_text)
            
            # Add contractor info and ensure types
            result['name'] = contractor['name']
            result['rating'] = contractor['rating']
            result['speed'] = contractor['speed']
            result['original_price'] = round(initial_quote, 2)
            result['final_price'] = float(result['final_price'])
            result['discount_percent'] = float(result['discount_percent'])
            result['deposit_required'] = float(result['deposit_required'])
            
            return result
            
        except Exception as e:
            logger.error(f"Groq error: {e}, using fallback")
            
            # Fallback
            discount = random.uniform(0.10, 0.20)
            final_price = initial_quote * (1 - discount)
            
            return {
                "name": contractor['name'],
                "final_price": round(final_price, 2),
                "original_price": round(initial_quote, 2),
                "discount_percent": round(discount * 100, 1),
                "eta": "45 minutes" if contractor['speed'] == 'fast' else "2 hours",
                "deposit_required": round(final_price * 0.2, 2),
                "rating": contractor['rating'],
                "speed": contractor['speed'],
                "negotiation_notes": f"Secured {round(discount*100)}% emergency discount"
            }