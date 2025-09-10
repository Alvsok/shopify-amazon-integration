import requests
import os
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

def test_production_sellers():
    """Test PRODUCTION Sellers API for real Australian store data"""
    access_token = get_access_token()
    
    # PRODUCTION endpoint (not sandbox!)
    url = "https://sellingpartnerapi-na.amazon.com/sellers/v1/marketplaceParticipations"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    print(f"PRODUCTION Sellers API Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n🇦🇺 Ваши РЕАЛЬНЫЕ данные магазина:")
        data = response.json()
        for participation in data.get('payload', []):
            marketplace = participation.get('marketplace', {})
            store_name = participation.get('storeName', 'N/A')
            
            print(f"Store Name: {store_name}")
            print(f"Marketplace ID: {marketplace.get('id', 'N/A')}")
            print(f"Country: {marketplace.get('countryCode', 'N/A')}")
            print(f"Domain: {marketplace.get('domainName', 'N/A')}")

if __name__ == "__main__":
    try:
        print("Тестируем PRODUCTION API с реальными данными...")
        test_production_sellers()
    except Exception as e:
        print(f"Error: {e}")