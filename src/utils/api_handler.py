"""
QuantEdge - API Handler Utility
Manages API interactions with various brokers.
"""

import requests
from typing import Dict, Optional
from datetime import datetime
import logging

class APIHandler:
    """Handles all API interactions with brokers."""
    
    def __init__(self, broker: str, api_key: Optional[str] = None):
        """
        Initialize API handler with broker credentials.
        
        Args:
            broker (str): Broker name
            api_key (str, optional): API key for authentication
        """
        self.broker = broker.lower()
        self.api_key = api_key
        self.base_urls = {
            'upstox': 'https://api.upstox.com/v2/',
            'fyers': 'https://api.fyers.in/api/v2/',
            'zerodha': 'https://api.kite.trade/'
        }
        self.session = requests.Session()
        self._setup_session()
        
    def _setup_session(self):
        """Configure API session with headers and authentication."""
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
    
    def fetch_option_chain(self, instrument_name: str, expiry_date: str, side: str) -> Dict:
        """
        Fetch option chain data from broker API.
        
        Args:
            instrument_name (str): Name of the instrument
            expiry_date (str): Expiry date
            side (str): Option type - CE/PE
            
        Returns:
            dict: Option chain data
        """
        endpoint = f"market-data/option-chain/{instrument_name}"
        params = {
            'expiry': expiry_date,
            'optionType': side
        }
        
        try:
            response = self.session.get(
                f"{self.base_urls[self.broker]}{endpoint}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error: {str(e)}")
            raise

    def fetch_margin_requirements(
        self,
        instrument_name: str,
        strike_price: float,
        side: str,
        qty: int,
        position_type: str
    ) -> Dict:
        """
        Fetch margin requirements from broker API.
        
        Args:
            instrument_name (str): Name of the instrument
            strike_price (float): Strike price
            side (str): Option type - CE/PE
            qty (int): Quantity
            position_type (str): Buy/Sell
            
        Returns:
            dict: Margin requirements
        """
        endpoint = "margin/required"
        payload = {
            'instrument': instrument_name,
            'strike': strike_price,
            'optionType': side,
            'quantity': qty,
            'positionType': position_type
        }
        
        try:
            response = self.session.post(
                f"{self.base_urls[self.broker]}{endpoint}",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error: {str(e)}")
            raise