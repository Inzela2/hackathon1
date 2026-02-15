from twilio.rest import Client
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def send_sms(to, message):
    """Send SMS notification via Twilio"""
    try:
        # Get Twilio credentials
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            logger.warning("Twilio not configured, simulating SMS")
            logger.info(f"📱 SIMULATED SMS to {to}:")
            logger.info(f"   {message}")
            return True
        
        # Send real SMS
        client = Client(account_sid, auth_token)
        
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to
        )
        
        logger.info(f"✓ SMS sent: {msg.sid}")
        return True
        
    except Exception as e:
        logger.error(f"SMS error: {e}")
        # In demo mode, log and continue
        logger.info(f"📱 FALLBACK SMS to {to}:")
        logger.info(f"   {message}")
        return True

def format_currency(amount, currency='AUD'):
    """Format currency for display"""
    return f"${amount:,.2f} {currency}"

def calculate_time_elapsed(start_time, end_time=None):
    """Calculate elapsed time between two timestamps"""
    if end_time is None:
        end_time = datetime.now()
    
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time)
    
    delta = end_time - start_time
    
    total_seconds = delta.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"

def validate_phone_number(phone):
    """Basic phone number validation"""
    import re
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Australian numbers should be 10 digits (mobile) or start with country code
    if len(digits) == 10:
        return f"+61{digits[1:]}"  # Convert to international format
    elif len(digits) == 11 and digits.startswith('61'):
        return f"+{digits}"
    elif len(digits) > 10:
        return f"+{digits}"
    
    # Return as-is if can't validate
    return phone

def generate_claim_summary(claim):
    """Generate a human-readable claim summary"""
    summary = f"""
CLAIM SUMMARY
═══════════════════════════════════════════════════════════
Claim ID: #{claim['id']}
Status: {claim['status'].upper()}
Created: {claim['timestamp']}

INCIDENT:
{claim['initial_message']}

ASSESSMENT:
- Damage Type: {claim['triage']['damage_type']}
- Severity: {claim['triage']['severity']}
- Safety Concern: {'Yes' if claim['triage']['safety_concern'] else 'No'}
"""
    
    if 'assessment' in claim:
        summary += f"""
DAMAGE ASSESSMENT:
- Estimated Cost: ${claim['assessment']['estimated_cost']:,.2f}
- Urgency: {claim['assessment']['urgency']}
- Required Trade: {claim['assessment']['required_trade']}
"""
    
    if 'contractor' in claim:
        summary += f"""
CONTRACTOR ASSIGNED:
- Company: {claim['contractor']['name']}
- Rating: {claim['contractor']['rating']}/5.0
- ETA: {claim['contractor']['eta']}
- Final Price: ${claim['contractor']['final_price']:,.2f}
"""
    
    if 'completion_time' in claim:
        start = datetime.fromisoformat(claim['timestamp'])
        end = datetime.fromisoformat(claim['completion_time'])
        elapsed = calculate_time_elapsed(start, end)
        summary += f"""
RESOLUTION TIME: {elapsed}
"""
    
    summary += "═══════════════════════════════════════════════════════════"
    
    return summary