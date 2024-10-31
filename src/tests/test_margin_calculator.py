"""
QuantEdge - Margin Calculator Tests
Unit tests for the MarginCalculator class.
"""

import unittest
from unittest.mock import Mock, patch
from src.margin_calculator import MarginCalculator

class TestMarginCalculator(unittest.TestCase):
    """Test cases for MarginCalculator class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.calculator = MarginCalculator(broker="upstox")
    
    @patch('src.utils.api_handler.APIHandler.fetch_margin_requirements')
    def test_calculate_position_margin(self, mock_fetch):
        """Test position margin calculation."""
        # Mock API response
        mock_fetch.return_value = {
            'span': 10000,
            'exposure': 5000
        }
        
        result = self.calculator.calculate_position_margin(
            instrument_name="NIFTY",
            strike_price=18000,
            side="CE",
            qty=1,
            position_type="sell"
        )
        
        self.assertEqual(result['total_margin'], 12500)
        self.assertEqual(result['span_margin'], 10000)
        self.assertEqual(result['exposure_margin'], 2500)

if __name__ == '__main__':
    unittest.main()