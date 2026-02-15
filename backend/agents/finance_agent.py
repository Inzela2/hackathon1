
"""
Finance Agent - SIMULATED PAYMENTS (100% FREE!)

No real payment processing for demo - just simulation.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FinanceAgent:
    """Handles payment processing - DEMO MODE (100% FREE!)"""
    
    def __init__(self):
        logger.info("💳 Finance Agent initialized (Simulation Mode - FREE!)")
        
    def process_payment(self, amount, contractor):
        """Process deposit payment (SIMULATED for demo)"""
        
        deposit = round(amount * 0.2, 2)  # 20% deposit
        payment_id = f"demo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"✓ Simulated payment: {payment_id}")
        logger.info(f"   Deposit: ${deposit:.2f}")
        logger.info(f"   Contractor: {contractor}")
        
        return {
            "success": True,
            "deposit": deposit,
            "total_cost": amount,
            "remaining": round(amount - deposit, 2),
            "payment_id": payment_id,
            "status": "deposit_paid_simulated",
            "contractor": contractor,
            "timestamp": datetime.now().isoformat()
        }