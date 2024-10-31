"""
QuantEdge - Data Fetcher Tests
Unit tests for the OptionsDataFetcher class.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import pandas as pd
from src.data_fetcher import OptionsDataFetcher

class TestOptionsDataFetcher(unittest.TestCase):
    """Test cases for OptionsDataFetcher class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.fetcher = OptionsDataFetcher(broker="upstox")
        
    def test_init(self):
        """Test initialization of OptionsDataFetcher."""
        self.assertEqual(self.fetcher.lot_sizes["NIFTY"], 50)
        self.assertEqual(self.fetcher.lot_sizes["BANKNIFTY"], 25)
    
    @patch('src.utils.api_handler.APIHandler.fetch_option_chain')
    def test_get_option_chain(self, mock_fetch):
        """Test option chain data retrieval."""
        # Mock API response
        mock_fetch.return_value = {
            'data': [{
                'strikePrice': 18000,
                'bidPrice': 100,
                'askPrice': 102,
                'bidQty': 500,
                'askQty': 500,
                'openInterest': 1000,
                'volume': 5000
            }]
        }
        
        result = self.fetcher.get_option_chain(
            instrument_name="NIFTY",
            expiry_date="2024-12-31",
            side="CE"
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['strike_price'], 18000)