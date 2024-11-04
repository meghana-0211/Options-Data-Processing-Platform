# src/utils/api_handler.py
import yaml
import os
import requests
from typing import Dict, Optional
import logging

class APIHandler:
    """Handles all API interactions with Upstox API."""
    
    def __init__(self, broker: str = "upstox"):
        """
        Initialize API handler with broker credentials.
        
        Args:
            broker (str): Broker name (default: upstox)
        """
        self.broker = broker.lower()
        self.config = self._load_config()
        self.session = requests.Session()
        self._setup_session()
        
    def _load_config(self) -> Dict:
        """Load API configuration from YAML file."""
        config_path = os.path.join('config', 'api_config.yaml')
        
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config[self.broker]
        except Exception as e:
            logging.error(f"Error loading config: {str(e)}")
            raise
        
    def _setup_session(self):
        """Configure API session with headers and authentication."""
        self.session.headers.update({
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.config["access_token"]}',
            'Content-Type': 'application/json'
        })
    
    def fetch_option_chain(self, instrument_name: str, expiry_date: str, side: str) -> Dict:
        """Fetch option chain data from Upstox API."""
        endpoint = f"{self.config['base_url']}/market-data/option-chain"
        
        params = {
            'symbol': f'NSE_FO|{instrument_name}',
            'expiry': expiry_date,
            'strike_price': 0,  # 0 means all strikes
            'option_type': side
        }
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error: {str(e)}")
            raise

    def fetch_margin_requirements(self, instrument_name: str, strike_price: float, 
                                side: str, qty: int, position_type: str) -> Dict:
        """Fetch margin requirements from Upstox API."""
        endpoint = f"{self.config['base_url']}/margin/charges"
        
        payload = {
            'instrument': f'NSE_FO|{instrument_name}',
            'quantity': qty,
            'product': 'I',  # Intraday
            'transaction_type': 'BUY' if position_type == 'buy' else 'SELL',
            'price': strike_price
        }
        
        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error: {str(e)}")
            raise

    def fetch_underlying_price(self, instrument_name: str) -> float:
        """Fetch current market price from Upstox API."""
        endpoint = f"{self.config['base_url']}/market-quote/ltp"
        
        params = {
            'symbol': f'NSE_EQ|{instrument_name}'
        }
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            return float(data['data']['last_price'])
        except requests.exceptions.RequestException as e:
            logging.error(f"API Error: {str(e)}")
            raise