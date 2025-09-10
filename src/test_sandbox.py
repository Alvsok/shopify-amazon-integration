import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment
AMAZON_CLIENT_ID = os.getenv('AMAZON_CLIENT_ID')
AMAZON_CLIENT_SECRET = os.getenv('AMAZON_CLIENT_SECRET')
AMAZON_REFRESH_TOKEN = os.getenv('AMAZON_REFRESH_TOKEN')

def get_access_token():
    """Get access token using refresh token"""
    url = "https://api.amazon.com/auth/o2/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': AMAZON_REFRESH_TOKEN,
        'client_id': AMAZON_CLIENT_ID,
        'client_secret': AMAZON_CLIENT_SECRET
    }
    
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def test_marketplaces():
    """Test getting marketplaces list"""
    access_token = get_access_token()
    
    url = "https://sandbox.sellingpartnerapi-na.amazon.com/sellers/v1/marketplaceParticipations"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    print(f"Marketplaces Status Code: {response.status_code}")
    print(f"Marketplaces Response: {response.text}")
    print()

def test_catalog_items():
    """Test getting catalog items with different ASINs"""
    access_token = get_access_token()
    
    # Different test ASINs to try
    test_asins = ["B007HIKFNH", "B00A2KD8NY", "B08N5WRWNW", "B0123456789"]
    
    for asin in test_asins:
        print(f"Testing ASIN: {asin}")
        url = f"https://sandbox.sellingpartnerapi-na.amazon.com/catalog/2022-04-01/items/{asin}"
        
        headers = {
            'x-amz-access-token': access_token,
            'Content-Type': 'application/json'
        }
        
        params = {
            'marketplaceIds': 'ATVPDKIKX0DER',
            'includedData': 'productTypes'
        }
        
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print("-" * 50)

if __name__ == "__main__":
    try:
        print("Testing marketplaces...")
        test_marketplaces()
        
        print("Testing catalog items...")
        test_catalog_items()
    except Exception as e:
        print(f"Error: {e}")