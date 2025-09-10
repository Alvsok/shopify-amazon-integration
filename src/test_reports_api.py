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

def get_report_types():
    """Get available report types"""
    access_token = get_access_token()
    
    url = "https://sandbox.sellingpartnerapi-na.amazon.com/reports/2021-06-30/reports"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    print(f"Reports Status Code: {response.status_code}")
    print(f"Response: {response.text}")

def create_inventory_report():
    """Create inventory report"""
    access_token = get_access_token()
    
    url = "https://sandbox.sellingpartnerapi-na.amazon.com/reports/2021-06-30/reports"
    
    headers = {
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    data = {
        "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
        "marketplaceIds": ["ATVPDKIKX0DER"]
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Create Report Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    try:
        print("Getting existing reports...")
        get_report_types()
        print("-" * 50)
        
        print("Creating inventory report...")
        create_inventory_report()
        
    except Exception as e:
        print(f"Error: {e}")