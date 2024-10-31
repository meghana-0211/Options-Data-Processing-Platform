"""
QuantEdge - Premium Analyzer
Handles premium calculations and analysis for options positions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from .utils.data_validator import DataValidator
from scipy.stats import norm

class PremiumAnalyzer:
    """
    Analyzes option premiums and calculates various metrics related to
    premium decay, potential returns, and risk metrics.
    """
    
    def __init__(self):
        """Initialize the PremiumAnalyzer with default parameters."""
        self.validator = DataValidator()
        self.risk_free_rate = 0.05  # 5% risk-free rate
        self.calendar = self._initialize_trading_calendar()
        
    def _initialize_trading_calendar(self) -> Dict[str, List[datetime]]:
        """
        Initialize trading calendar with holidays and trading days.
        
        Returns:
            dict: Calendar with holidays and trading days
        """
        # This would typically be loaded from a database or external source
        return {
            'holidays': [],
            'trading_days': []
        }
        
    def calculate_premium_metrics(
        self,
        current_price: float,
        strike_price: float,
        days_to_expiry: int,
        volatility: float,
        side: str,
        lot_size: int
    ) -> Dict[str, float]:
        """
        Calculate comprehensive premium metrics for an option position.
        
        Args:
            current_price (float): Current price of the underlying
            strike_price (float): Strike price of the option
            days_to_expiry (int): Number of days to expiry
            volatility (float): Implied volatility
            side (str): Option type - 'CE' or 'PE'
            lot_size (int): Number of shares per lot
            
        Returns:
            dict: Dictionary containing various premium metrics
        """
        # Validate inputs
        self.validator.validate_premium_inputs(
            current_price=current_price,
            strike_price=strike_price,
            days_to_expiry=days_to_expiry,
            volatility=volatility,
            side=side,
            lot_size=lot_size
        )
        
        # Calculate option Greeks
        greeks = self._calculate_greeks(
            current_price,
            strike_price,
            days_to_expiry,
            volatility,
            side
        )
        
        # Calculate premium and related metrics
        premium = self._calculate_theoretical_premium(
            current_price,
            strike_price,
            days_to_expiry,
            volatility,
            side
        )
        
        total_premium = premium * lot_size
        
        # Calculate daily theta decay
        daily_decay = abs(greeks['theta'])
        
        # Calculate potential returns
        max_profit = self._calculate_max_profit(premium, strike_price, side)
        max_loss = self._calculate_max_loss(premium, strike_price, side)
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(
            premium,
            max_profit,
            max_loss,
            volatility
        )
        
        return {
            'premium': premium,
            'total_premium': total_premium,
            'daily_theta_decay': daily_decay,
            'greeks': greeks,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'risk_metrics': risk_metrics
        }
        
    def _calculate_theoretical_premium(
        self,
        current_price: float,
        strike_price: float,
        days_to_expiry: int,
        volatility: float,
        side: str
    ) -> float:
        """
        Calculate theoretical option premium using Black-Scholes model.
        
        Args:
            current_price (float): Current price of underlying
            strike_price (float): Strike price of option
            days_to_expiry (int): Days to expiry
            volatility (float): Implied volatility
            side (str): Option type - CE/PE
            
        Returns:
            float: Theoretical option premium
        """
        T = days_to_expiry / 365.0
        sigma = volatility
        S = current_price
        K = strike_price
        r = self.risk_free_rate
        
        d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        
        if side == 'CE':
            premium = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        else:  # PE
            premium = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
            
        return float(premium)
        
    def _calculate_greeks(
        self,
        current_price: float,
        strike_price: float,
        days_to_expiry: int,
        volatility: float,
        side: str
    ) -> Dict[str, float]:
        """
        Calculate option Greeks.
        
        Args:
            current_price (float): Current price of underlying
            strike_price (float): Strike price of option
            days_to_expiry (int): Days to expiry
            volatility (float): Implied volatility
            side (str): Option type - CE/PE
            
        Returns:
            dict: Dictionary containing Greeks (delta, gamma, theta, vega)
        """
        T = days_to_expiry / 365.0
        sigma = volatility
        S = current_price
        K = strike_price
        r = self.risk_free_rate
        
        d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        
        # Calculate Greeks
        if side == 'CE':
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1
            
        gamma = norm.pdf(d1)/(S*sigma*np.sqrt(T))
        
        theta = (-S*norm.pdf(d1)*sigma)/(2*np.sqrt(T)) - \
                r*K*np.exp(-r*T)*norm.cdf(d2) if side == 'CE' else \
                (-S*norm.pdf(d1)*sigma)/(2*np.sqrt(T)) + \
                r*K*np.exp(-r*T)*norm.cdf(-d2)
                
        vega = S*np.sqrt(T)*norm.pdf(d1)
        
        return {
            'delta': float(delta),
            'gamma': float(gamma),
            'theta': float(theta),
            'vega': float(vega)
        }
        
    def _calculate_max_profit(
        self,
        premium: float,
        strike_price: float,
        side: str
    ) -> float:
        """
        Calculate maximum potential profit.
        
        Args:
            premium (float): Option premium
            strike_price (float): Strike price
            side (str): Option type - CE/PE
            
        Returns:
            float: Maximum potential profit
        """
        if side == 'CE':
            return float('inf')  # Unlimited profit potential for calls
        else:
            return max(0, strike_price - premium)
            
    def _calculate_max_loss(
        self,
        premium: float,
        strike_price: float,
        side: str
    ) -> float:
        """
        Calculate maximum potential loss.
        
        Args:
            premium (float): Option premium
            strike_price (float): Strike price
            side (str): Option type - CE/PE
            
        Returns:
            float: Maximum potential loss
        """
        return premium  # Maximum loss is premium paid
        
    def _calculate_risk_metrics(
        self,
        premium: float,
        max_profit: float,
        max_loss: float,
        volatility: float
    ) -> Dict[str, float]:
        """
        Calculate risk metrics for the position.
        
        Args:
            premium (float): Option premium
            max_profit (float): Maximum profit
            max_loss (float): Maximum loss
            volatility (float): Implied volatility
            
        Returns:
            dict: Risk metrics including Sharpe ratio and risk/reward ratio
        """
        # Calculate risk/reward ratio
        risk_reward_ratio = abs(max_loss / max_profit) if max_profit != float('inf') else 0
        
        # Calculate annualized return potential
        annual_return_potential = (max_profit - premium) / premium * 100
        
        # Calculate volatility-adjusted return
        vol_adjusted_return = annual_return_potential / volatility
        
        return {
            'risk_reward_ratio': float(risk_reward_ratio),
            'annual_return_potential': float(annual_return_potential),
            'volatility_adjusted_return': float(vol_adjusted_return)
        }
        
    def analyze_premium_decay(
        self,
        premium_metrics: Dict,
        time_points: List[int]
    ) -> pd.DataFrame:
        """
        Analyze premium decay over time.
        
        Args:
            premium_metrics (dict): Current premium metrics
            time_points (list): List of days to analyze
            
        Returns:
            pd.DataFrame: Premium decay analysis
        """
        decay_data = []
        
        for days in time_points:
            theta_decay = premium_metrics['daily_theta_decay'] * days
            remaining_premium = max(0, premium_metrics['pre mium'] - theta_decay)
            
            decay_data.append({
                'days': days,
                'premium': remaining_premium,
                'decay_amount': theta_decay,
                'decay_percentage': (theta_decay / premium_metrics['premium']) * 100
            })
            
        return pd.DataFrame(decay_data)