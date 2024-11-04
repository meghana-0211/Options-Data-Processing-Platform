# main.py
from src.data_fetcher import OptionsDataFetcher
from src.margin_calculator import MarginCalculator
import pandas as pd
from datetime import datetime, timedelta

def main():
    # Initialize the fetcher
    fetcher = OptionsDataFetcher(broker="upstox")
    
    # Get today's date
    today = datetime.now()
    
    # Get next monthly expiry (last Thursday of the month)
    current_month = today.replace(day=28)
    while current_month.weekday() != 3:  # 3 is Thursday
        current_month += timedelta(days=1)
    expiry_date = current_month.strftime("%Y-%m-%d")
    
    try:
        # Fetch NIFTY options chain
        print("Fetching NIFTY options chain...")
        nifty_options = fetcher.get_option_chain(
            instrument_name="NIFTY",
            expiry_date=expiry_date,
            side="CE"
        )
        
        print("\nOptions Chain Data:")
        print(nifty_options.head())
        
        # Calculate margins for a sample position
        calculator = MarginCalculator(broker="upstox")
        margin_info = calculator.calculate_position_margin(
            instrument_name="NIFTY",
            strike_price=20000,  # Example strike price
            side="CE",
            qty=1,
            position_type="sell"
        )
        
        print("\nMargin Requirements:")
        print(f"Total Margin: ₹{margin_info['total_margin']:,.2f}")
        print(f"SPAN Margin: ₹{margin_info['span_margin']:,.2f}")
        print(f"Exposure Margin: ₹{margin_info['exposure_margin']:,.2f}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()