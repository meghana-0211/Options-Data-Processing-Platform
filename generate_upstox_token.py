# generate_upstox_token.py
from upstox_python import Upstox
import yaml

def generate_upstox_token():
    # Replace these with your actual Upstox API credentials
    api_key = "YOUR_API_KEY"
    api_secret = "YOUR_API_SECRET"
    redirect_uri = "YOUR_REDIRECT_URI"

    # Initialize Upstox client
    upstox_client = Upstox(api_key, redirect_uri)

    # Generate login URL
    login_url = upstox_client.get_login_url()
    print("Please visit the URL and authorize the app:")
    print(login_url)

    # After authorization, you'll receive an authorization code
    authorization_code = input("Enter the authorization code from the redirect URL: ")

    # Get access token
    access_token = upstox_client.get_access_token(authorization_code, api_secret)

    # Update config file
    config = {
        'upstox': {
            'api_key': api_key,
            'api_secret': api_secret,
            'redirect_uri': redirect_uri,
            'access_token': access_token
        }
    }

    # Save to config file
    with open('config/api_config.yaml', 'w') as file:
        yaml.dump(config, file)

    print("Access token generated and saved to api_config.yaml")

if __name__ == "__main__":
    generate_upstox_token()