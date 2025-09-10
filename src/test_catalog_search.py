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

def test_catalog_search():
    """Test catalog search instead of specific item lookup"""
    access_token = get_access_token()
    
    url = "https://sandbox.sellingpartnerapi-na.amazon.com/catalog/2022-04-01/items"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    params = {
        'marketplaceIds': 'ATVPDKIKX0DER',
        'keywords': 'book',
        'includedData': 'productTypes',
        'pageSize': 5
    }
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Catalog Search Status Code: {response.status_code}")
    print(f"Response: {response.text}")

def test_product_type_definitions():
    """Test getting product type definitions"""
    access_token = get_access_token()
    
    url = "https://sandbox.sellingpartnerapi-na.amazon.com/definitions/2020-09-01/productTypes"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    params = {
        'marketplaceIds': 'ATVPDKIKX0DER'
    }
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Product Types Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    try:
        print("Testing catalog search...")
        test_catalog_search()
        print("-" * 50)
        
        print("Testing product type definitions...")
        test_product_type_definitions()
    except Exception as e:
        print(f"Error: {e}")