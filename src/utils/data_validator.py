"""
QuantEdge - Data Validator Utility
Validates input data and parameters.
"""

from typing import Dict, Optional
from datetime import datetime
import re

class DataValidator:
    """Validates input data for various operations."""
    
    def __init__(self):
        """Initialize validator with common validation patterns."""
        self.patterns = {
            'instrument': r'^[A-Z]+$',
            'date': r'^\d{4}-\d{2}-\d{2}$'
        }
    
    def validate_inputs(
        self,
        instrument_name: str,
        expiry_date: str,
        side: str,
        strike_range: Optional[Dict[str, float]] = None
    ) -> None:
        """
        Validate input parameters for option chain data.
        
        Args:
            instrument_name (str): Name of the instrument
            expiry_date (str): Expiry date
            side (str): Option type
            strike_range (dict, optional): Strike price range
            
        Raises:
            ValueError: If validation fails
        """
        # Validate instrument name
        if not re.match(self.patterns['instrument'], instrument_name):
            raise ValueError("Invalid instrument name format")
        
        # Validate expiry date
        if not re.match(self.patterns['date'], expiry_date):
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
            
        # Validate expiry date is in future
        if datetime.strptime(expiry_date, "%Y-%m-%d") < datetime.now():
            raise ValueError("Expiry date must be in the future")
        
        # Validate option type
        if side not in ['CE', 'PE']:
            raise ValueError("Side must be either 'CE' or 'PE'")
        
        # Validate strike range if provided
        if strike_range:
            if not all(k in strike_range for k in ['lower', 'upper']):
                raise ValueError("Strike range must include 'lower' and 'upper' bounds")
            if strike_range['lower'] >= strike_range['upper']:
                raise ValueError("Upper bound must be greater than lower bound")

    def validate_margin_inputs(
        self,
        instrument_name: str,
        strike_price: float,
        side: str,
        qty: int,
        position_type: str
    ) -> None:
        """
        Validate input parameters for margin calculations.
        
        Args:
            instrument_name (str): Name of the instrument
            strike_price (float): Strike price
            side (str): Option type
            qty (int): Quantity
            position_type (str): Position type
            
        Raises:
            ValueError: If validation fails
        """
        if not re.match(self.patterns['instrument'], instrument_name):
            raise ValueError("Invalid instrument name format")
            
        if strike_price <= 0:
            raise ValueError("Strike price must be positive")
            
        if side not in ['CE', 'PE']:
            raise ValueError("Side must be either 'CE' or 'PE'")
            
        if qty <= 0:
            raise ValueError("Quantity must be positive")
            
        if position_type not in ['buy', 'sell']:
            raise ValueError("Position type must be either 'buy' or 'sell'")
