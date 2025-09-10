import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment
AMAZON_CLIENT_ID = os.getenv('AMAZON_CLIENT_ID')
AMAZON_CLIENT_SECRET = os.getenv('AMAZON_CLIENT_SECRET')
AMAZON_REFRESH_TOKEN = os.getenv('AMAZON_REFRESH_TOKEN')

# Hardcoded ASIN (sandbox test ASIN)
asin = "B007HIKFNH"

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

def get_product_type(asin):
    """Get productType for given ASIN"""
    access_token = get_access_token()
    
    # Use sandbox endpoint
    url = f"https://sandbox.sellingpartnerapi-na.amazon.com/catalog/2022-04-01/items/{asin}"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    params = {
        'marketplaceIds': 'ATVPDKIKX0DER',  # US marketplace for sandbox
        'includedData': 'productTypes'
    }
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Text: {response.text}")
    
    response.raise_for_status()
    data = response.json()
    
    if 'productTypes' in data:
        return data['productTypes'][0]['productType']
    else:
        return None

if __name__ == "__main__":
    try:
        product_type = get_product_type(asin)
        print(f"ASIN: {asin}")
        print(f"Product Type: {product_type}")
    except Exception as e:
        print(f"Error: {e}")