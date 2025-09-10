import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

AMAZON_CLIENT_ID = os.getenv('AMAZON_CLIENT_ID')
AMAZON_CLIENT_SECRET = os.getenv('AMAZON_CLIENT_SECRET')
AMAZON_REFRESH_TOKEN = os.getenv('AMAZON_REFRESH_TOKEN')

def get_access_token():
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

def get_marketplace_participations():
    """Get detailed marketplace participation info"""
    access_token = get_access_token()
    
    url = "https://sandbox.sellingpartnerapi-na.amazon.com/sellers/v1/marketplaceParticipations"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    print(f"=== Marketplace Participations ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Raw Response: {json.dumps(data, indent=2)}")
        
        for participation in data.get('payload', []):
            marketplace = participation.get('marketplace', {})
            store_name = participation.get('storeName', 'N/A')
            participation_info = participation.get('participation', {})
            
            print(f"\n--- Store Information ---")
            print(f"Store Name: {store_name}")
            print(f"Marketplace ID: {marketplace.get('id', 'N/A')}")
            print(f"Country: {marketplace.get('countryCode', 'N/A')}")
            print(f"Domain: {marketplace.get('domainName', 'N/A')}")
            print(f"Is Participating: {participation_info.get('isParticipating', 'N/A')}")
            print(f"Has Suspended Listings: {participation_info.get('hasSuspendedListings', 'N/A')}")
    else:
        print(f"Error: {response.text}")
    
    return response

def check_orders_api():
    """Check if Orders API reveals seller ID"""
    access_token = get_access_token()
    
    url = "https://sandbox.sellingpartnerapi-na.amazon.com/orders/v0/orders"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    params = {
        'MarketplaceIds': 'ATVPDKIKX0DER',
        'CreatedAfter': '2023-01-01T00:00:00Z'
    }
    
    response = requests.get(url, headers=headers, params=params)
    print(f"\n=== Orders API ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

def check_application_info():
    """Check application information that might contain seller info"""
    access_token = get_access_token()
    
    # Try different endpoints that might reveal seller ID
    endpoints_to_try = [
        "/applications/2023-11-30/applications",
        "/applications/v1/applications", 
        "/seller/v1/account"
    ]
    
    for endpoint in endpoints_to_try:
        url = f"https://sandbox.sellingpartnerapi-na.amazon.com{endpoint}"
        
        headers = {
            'x-amz-access-token': access_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        print(f"\n=== {endpoint} ===")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    try:
        # Get detailed marketplace info
        get_marketplace_participations()
        
        # Try Orders API
        check_orders_api()
        
        # Try to find seller ID in other endpoints
        check_application_info()
        
    except Exception as e:
        print(f"Error: {e}")