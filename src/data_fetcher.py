"""
QuantEdge - Options Chain Data Retriever
Handles the retrieval and initial processing of options chain data from various Indian brokers' APIs.
"""

import pandas as pd
import requests
from datetime import datetime
from typing import Dict, Optional, Union, List
from .utils.api_handler import APIHandler
from .utils.data_validator import DataValidator

class OptionsDataFetcher:
    """
    A class to handle fetching and processing options chain data from various brokers' APIs.
    Supports multiple Indian brokers including Upstox, Fyers, and Zerodha.
    """
    
    def __init__(self, broker: str = "upstox", api_key: Optional[str] = None):
        """
        Initialize the OptionsDataFetcher with specific broker and credentials.
        
        Args:
            broker (str): Name of the broker (upstox/fyers/zerodha)
            api_key (str, optional): API key for authentication
        """
        self.api_handler = APIHandler(broker, api_key)
        self.validator = DataValidator()
        self.lot_sizes = {
            "NIFTY": 50,
            "BANKNIFTY": 25,
            "FINNIFTY": 40
        }

    def get_option_chain(
        self,
        instrument_name: str,
        expiry_date: str,
        side: str,
        strike_range: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Fetch option chain data for specified parameters.
        
        Args:
            instrument_name (str): Name of the instrument (e.g., NIFTY, BANKNIFTY)
            expiry_date (str): Expiry date in YYYY-MM-DD format
            side (str): Option type - 'CE' or 'PE'
            strike_range (dict, optional): Range of strikes to fetch {'lower': float, 'upper': float}
        
        Returns:
            pd.DataFrame: Processed options chain data
        """
        # Validate inputs
        self.validator.validate_inputs(
            instrument_name=instrument_name,
            expiry_date=expiry_date,
            side=side,
            strike_range=strike_range
        )

        # Fetch raw data from API
        raw_data = self.api_handler.fetch_option_chain(
            instrument_name,
            expiry_date,
            side
        )

        # Process the data
        processed_data = self._process_option_chain(raw_data, side, strike_range)
        
        return processed_data

    def _process_option_chain(
        self,
        raw_data: Dict,
        side: str,
        strike_range: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Process raw option chain data into a structured DataFrame.
        
        Args:
            raw_data (dict): Raw API response data
            side (str): Option type - 'CE' or 'PE'
            strike_range (dict, optional): Strike price range to filter
        
        Returns:
            pd.DataFrame: Processed data with relevant columns
        """
        # Extract relevant fields
        options_data = []
        
        for option in raw_data.get('data', []):
            strike_price = float(option.get('strikePrice', 0))
            
            # Apply strike range filter if provided
            if strike_range:
                if (strike_price < strike_range['lower'] or 
                    strike_price > strike_range['upper']):
                    continue
            
            # Extract price based on option type
            price = (option.get('bidPrice', 0) if side == 'PE' 
                    else option.get('askPrice', 0))
            
            options_data.append({
                'strike_price': strike_price,
                'bid_price': option.get('bidPrice', 0),
                'ask_price': option.get('askPrice', 0),
                'bid_qty': option.get('bidQty', 0),
                'ask_qty': option.get('askQty', 0),
                'oi': option.get('openInterest', 0),
                'volume': option.get('volume', 0),
                'iv': option.get('impliedVolatility', 0),
                'delta': option.get('delta', 0),
                'theta': option.get('theta', 0),
                'vega': option.get('vega', 0),
                'gamma': option.get('gamma', 0)
            })
        
        # Create DataFrame
        df = pd.DataFrame(options_data)
        
        # Add calculated columns
        df['price'] = price
        df['side'] = side
        df['timestamp'] = datetime.now().isoformat()
        
        return df

    def get_underlying_price(self, instrument_name: str) -> float:
        """
        Fetch current market price of the underlying instrument.
        
        Args:
            instrument_name (str): Name of the instrument
            
        Returns:
            float: Current market price
        """
        return self.api_handler.fetch_underlying_price(instrument_name)

    def get_historical_data(
        self,
        instrument_name: str,
        strike_price: float,
        side: str,
        from_date: str,
        to_date: str
    ) -> pd.DataFrame:
        """
        Fetch historical options data for analysis.
        
        Args:
            instrument_name (str): Name of the instrument
            strike_price (float): Strike price of the option
            side (str): Option type - 'CE' or 'PE'
            from_date (str): Start date in YYYY-MM-DD format
            to_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Historical options data
        """
        raw_data = self.api_handler.fetch_historical_data(
            instrument_name,
            strike_price,
            side,
            from_date,
            to_date
        )
        
        return self._process_historical_data(raw_data)

    def _process_historical_data(self, raw_data: Dict) -> pd.DataFrame:
        """
        Process historical data into a structured format.
        
        Args:
            raw_data (dict): Raw historical data from API
            
        Returns:
            pd.DataFrame: Processed historical data
        """
        historical_data = []
        
        for record in raw_data.get('data', []):
            historical_data.append({
                'date': record.get('date'),
                'open': record.get('open'),
                'high': record.get('high'),
                'low': record.get('low'),
                'close': record.get('close'),
                'volume': record.get('volume'),
                'oi': record.get('openInterest')
            })
        
        return pd.DataFrame(historical_data)

    def get_lot_size(self, instrument_name: str) -> int:
        """
        Get the lot size for the specified instrument.
        
        Args:
            instrument_name (str): Name of the instrument
            
        Returns:
            int: Lot size for the instrument
        """
        return self.lot_sizes.get(instrument_name.upper(), 0)