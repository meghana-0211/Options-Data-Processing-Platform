"""
QuantEdge - Margin Calculator
Handles margin calculations for options trading positions.
"""

from typing import Dict, List, Optional, Union
import pandas as pd
from utils.api_handler import APIHandler
from utils.data_validator import DataValidator

class MarginCalculator:
    """
    Calculates required margins for options trading positions with support
    for SPAN and exposure margins as per exchange requirements.
    """
    
    def __init__(self, broker: str = "upstox"):
        """
        Initialize the MarginCalculator with broker-specific configurations.
        
        Args:
            broker (str): Name of the broker for margin calculations
        """
        self.api_handler = APIHandler(broker)
        self.validator = DataValidator()
        
        # Standard margin multipliers
        self.margin_multipliers = {
            'nfo': 1.0,  # National Futures & Options
            'exposure': 0.5,  # Exposure margin
            'span': 1.0,  # SPAN margin
        }

    def calculate_position_margin(
        self,
        instrument_name: str,
        strike_price: float,
        side: str,
        qty: int,
        position_type: str = "sell"
    ) -> Dict[str, float]:
        """
        Calculate total margin required for an options position.
        
        Args:
            instrument_name (str): Name of the instrument
            strike_price (float): Strike price of the option
            side (str): Option type - 'CE' or 'PE'
            qty (int): Number of lots
            position_type (str): Type of position - 'buy' or 'sell'
            
        Returns:
            dict: Breakdown of different margin components
        """
        # Validate inputs
        self.validator.validate_margin_inputs(
            instrument_name=instrument_name,
            strike_price=strike_price,
            side=side,
            qty=qty,
            position_type=position_type
        )
        
        # Fetch margin requirements from broker API
        raw_margin = self.api_handler.fetch_margin_requirements(
            instrument_name,
            strike_price,
            side,
            qty,
            position_type
        )
        
        # Calculate different margin components
        span_margin = raw_margin.get('span', 0) * self.margin_multipliers['span']
        exposure_margin = raw_margin.get('exposure', 0) * self.margin_multipliers['exposure']
        
        # Calculate total margin
        total_margin = span_margin + exposure_margin
        
        return {
            'total_margin': total_margin,
            'span_margin': span_margin,
            'exposure_margin': exposure_margin,
            'breakdown': {
                'span_multiplier': self.margin_multipliers['span'],
                'exposure_multiplier': self.margin_multipliers['exposure'],
                'raw_span': raw_margin.get('span', 0),
                'raw_exposure': raw_margin.get('exposure', 0)
            }
        }

    def calculate_portfolio_margin(
        self,
        positions: List[Dict[str, Union[str, float, int]]]
    ) -> Dict[str, float]:
        """
        Calculate total margin required for a portfolio of positions.
        
        Args:
            positions (list): List of position dictionaries containing position details
            
        Returns:
            dict: Portfolio margin requirements with breakdown
        """
        total_margin = 0
        margin_details = []
        
        for position in positions:
            margin = self.calculate_position_margin(
                instrument_name=position['instrument_name'],
                strike_price=position['strike_price'],
                side=position['side'],
                qty=position['qty'],
                position_type=position.get('position_type', 'sell')
            )
            
            total_margin += margin['total_margin']
            margin_details.append({
                'position': position,
                'margin_details': margin
            })
        
        return {
            'total_portfolio_margin': total_margin,
            'position_details': margin_details
        }

    def estimate_margin_impact(
        self,
        current_positions: List[Dict],
        new_position: Dict
    ) -> Dict[str, float]:
        """
        Estimate the marginal impact of adding a new position to existing portfolio.
        
        Args:
            current_positions (list): List of current position dictionaries
            new_position (dict): New position to be added
            
        Returns:
            dict: Margin impact analysis
        """
        # Calculate current portfolio margin
        current_margin = self.calculate_portfolio_margin(current_positions)
        
        # Calculate new portfolio margin
        new_positions = current_positions + [new_position]
        new_margin = self.calculate_portfolio_margin(new_positions)
        
        # Calculate margin impact
        margin_impact = new_margin['total_portfolio_margin'] - current_margin['total_portfolio_margin']
        
        return {
            'current_margin': current_margin['total_portfolio_margin'],
            'new_margin': new_margin['total_portfolio_margin'],
            'margin_impact': margin_impact,
            'percentage_increase': (margin_impact / current_margin['total_portfolio_margin']) * 100
        }

    def get_margin_history(
        self,
        position: Dict,
        days: int = 30
    ) -> pd.DataFrame:
        """
        Get historical margin requirements for analysis.
        
        Args:
            position (dict): Position details
            days (int): Number of historical days to analyze
            
        Returns:
            pd.DataFrame: Historical margin requirements
        """
        raw_history = self.api_handler.fetch_margin_history(position, days)
        
        history_data = []
        for record in raw_history:
            history_data.append({
                'date': record['date'],
                'span_margin': record['span_margin'],
                'exposure_margin': record['exposure_margin'],
                'total_margin': record['total_margin']
            })
            
        return pd.DataFrame(history_data)
