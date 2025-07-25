import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any
import json

class PayoutSimulator:
    """Simulates payout processing for demo purposes"""
    
    def __init__(self):
        self.gv_codes = []
        self.upi_utrs = []
    
    def generate_gift_card_code(self, amount: float) -> str:
        """Generate a dummy Amazon Gift Card code"""
        # Format: XXXX-XXXX-XXXX-XXXX
        code = '-'.join([''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)])
        self.gv_codes.append({
            'code': code,
            'amount': amount,
            'generated_at': datetime.utcnow().isoformat(),
            'status': 'active'
        })
        return code
    
    def generate_upi_utr(self, amount: float) -> str:
        """Generate a dummy UPI UTR number"""
        # Format: UTR + 12 digits
        utr = 'UTR' + ''.join(random.choices(string.digits, k=12))
        self.upi_utrs.append({
            'utr': utr,
            'amount': amount,
            'generated_at': datetime.utcnow().isoformat(),
            'status': 'success'
        })
        return utr
    
    def process_payout(self, amount: float, method: str) -> Dict[str, Any]:
        """Process a payout and return receipt"""
        if method.lower() == 'gift_card':
            code = self.generate_gift_card_code(amount)
            return {
                'status': 'completed',
                'method': 'gift_card',
                'reference_id': code,
                'amount': amount,
                'receipt': {
                    'type': 'Amazon Gift Card',
                    'code': code,
                    'amount': f"₹{amount:,.2f}",
                    'valid_until': (datetime.utcnow() + timedelta(days=365)).strftime('%Y-%m-%d'),
                    'terms': 'Valid on Amazon.in for all purchases'
                }
            }
        elif method.lower() == 'upi':
            utr = self.generate_upi_utr(amount)
            return {
                'status': 'completed',
                'method': 'upi',
                'reference_id': utr,
                'amount': amount,
                'receipt': {
                    'type': 'UPI Transfer',
                    'utr': utr,
                    'amount': f"₹{amount:,.2f}",
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'Success'
                }
            }
        else:
            raise ValueError(f"Unsupported payout method: {method}")
    
    def get_payout_history(self) -> Dict[str, Any]:
        """Get payout history for demo"""
        return {
            'gift_cards': self.gv_codes,
            'upi_transfers': self.upi_utrs,
            'total_processed': len(self.gv_codes) + len(self.upi_utrs)
        }

# Global instance
payout_simulator = PayoutSimulator() 