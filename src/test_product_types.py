import requests
import os
import json
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

def get_all_product_types():
    """Get all available product types in sandbox"""
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
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Available product types: {len(data['productTypes'])}")
        for pt in data['productTypes']:
            print(f"  - {pt['name']}: {pt['displayName']}")
        return data['productTypes']
    else:
        print(f"Error: {response.text}")
        return None

def get_product_type_definition(product_type_name):
    """Get detailed definition for a specific product type"""
    access_token = get_access_token()
    
    url = f"https://sandbox.sellingpartnerapi-na.amazon.com/definitions/2020-09-01/productTypes/{product_type_name}"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    params = {
        'marketplaceIds': 'ATVPDKIKX0DER',
        'requirements': 'LISTING'
    }
    
    response = requests.get(url, headers=headers, params=params)
    print(f"\nProduct Type '{product_type_name}' Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Schema structure available!")
        # Don't print the full schema as it's very large
        if 'schema' in data:
            print(f"Schema properties count: {len(data['schema'].get('properties', {}))}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    try:
        print("Getting all product types...")
        product_types = get_all_product_types()
        
        if product_types:
            # Test getting definition for the first product type
            first_type = product_types[0]['name']
            get_product_type_definition(first_type)
            
    except Exception as e:
        print(f"Error: {e}")