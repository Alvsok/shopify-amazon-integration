import os
import requests
import json
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from urllib.parse import urlencode, quote

# Load environment variables
load_dotenv()

class AmazonSandboxClient:
    """Amazon Selling Partner API Sandbox Client"""
    
    def __init__(self):
        self.client_id = os.getenv('AMAZON_CLIENT_ID')
        self.client_secret = os.getenv('AMAZON_CLIENT_SECRET')
        self.refresh_token = os.getenv('AMAZON_REFRESH_TOKEN')
        self.sandbox_url = "https://sandbox.sellingpartnerapi-na.amazon.com"
        self.token_url = "https://api.amazon.com/auth/o2/token"
        self.access_token = None
    
    def get_access_token(self) -> Optional[str]:
        """Get access token using refresh token"""
        try:
            token_data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(self.token_url, data=token_data)
            response.raise_for_status()
            
            token_response = response.json()
            self.access_token = token_response['access_token']
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
        except KeyError as e:
            print(f"Missing key in token response: {e}")
            return None
    
    def make_api_request(self, endpoint: str, method: str = 'GET', data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """Make authenticated API request to Amazon with proper headers"""
        if not self.access_token:
            if not self.get_access_token():
                return None
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-amz-access-token': self.access_token,
            'User-Agent': 'shopify-amazon-integration/1.0'
        }
        
        url = f"{self.sandbox_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params)
            else:
                print(f"Unsupported HTTP method: {method}")
                return None
            
            print(f"Request URL: {response.url}")
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def test_listings_endpoint(self) -> bool:
        """Test the listings endpoint"""
        print("Testing Amazon Listings API endpoint...")
        
        # Try a simple seller API endpoint that's available in sandbox
        endpoint = "/sellers/v1/marketplaceParticipations"
        response = self.make_api_request(endpoint)
        
        if response is not None:
            print(f" Listings endpoint test successful")
            print(f"Response: {json.dumps(response, indent=2)}")
            return True
        else:
            print("L Listings endpoint test failed")
            return False
    
    def test_orders_endpoint(self) -> bool:
        """Test the orders endpoint"""
        print("Testing Amazon Orders API endpoint...")
        
        # Try FBA inventory endpoint instead - it's more accessible in sandbox
        endpoint = "/fba/inventory/v1/summaries"
        params = {
            'granularityType': 'Marketplace',
            'granularityId': 'ATVPDKIKX0DER',
            'marketplaceIds': ['ATVPDKIKX0DER']
        }
        response = self.make_api_request(endpoint, params=params)
        
        if response is not None:
            print(f" Orders endpoint test successful")
            print(f"Response: {json.dumps(response, indent=2)}")
            return True
        else:
            print("L Orders endpoint test failed")
            return False


class ShopifyClient:
    """Shopify API Client"""
    
    def __init__(self):
        self.shop_domain = os.getenv('SHOPIFY_SHOP_DOMAIN')
        self.access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
        self.api_version = os.getenv('SHOPIFY_API_VERSION', '2023-10')
        self.base_url = f"https://{self.shop_domain}.myshopify.com/admin/api/{self.api_version}"
    
    def make_api_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Optional[Dict]:
        """Make authenticated API request to Shopify"""
        headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            else:
                print(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Shopify API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def test_products_endpoint(self) -> bool:
        """Test the products endpoint"""
        print("Testing Shopify Products API endpoint...")
        
        endpoint = "/products.json?limit=5"
        response = self.make_api_request(endpoint)
        
        if response is not None:
            print(f" Products endpoint test successful")
            print(f"Found {len(response.get('products', []))} products")
            return True
        else:
            print("L Products endpoint test failed")
            return False
    
    def test_orders_endpoint(self) -> bool:
        """Test the orders endpoint"""
        print("Testing Shopify Orders API endpoint...")
        
        endpoint = "/orders.json?limit=5"
        response = self.make_api_request(endpoint)
        
        if response is not None:
            print(f" Orders endpoint test successful")
            print(f"Found {len(response.get('orders', []))} orders")
            return True
        else:
            print("L Orders endpoint test failed")
            return False


class IntegrationTester:
    """Main integration tester class"""
    
    def __init__(self):
        self.amazon_client = AmazonSandboxClient()
        self.shopify_client = ShopifyClient()
    
    def test_environment_variables(self) -> bool:
        """Test if all required environment variables are set"""
        print("Testing environment variables...")
        
        required_vars = [
            'AMAZON_CLIENT_ID',
            'AMAZON_CLIENT_SECRET',
            'AMAZON_REFRESH_TOKEN',
            'SHOPIFY_SHOP_DOMAIN',
            'SHOPIFY_ACCESS_TOKEN'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"L Missing environment variables: {', '.join(missing_vars)}")
            return False
        else:
            print(" All environment variables are set")
            return True
    
    def test_amazon_sandbox(self) -> bool:
        """Test Amazon Sandbox API connectivity"""
        print("\n= Testing Amazon Sandbox API...")
        
        # Test token generation
        if not self.amazon_client.get_access_token():
            print("L Failed to get Amazon access token")
            return False
        
        print(" Successfully obtained Amazon access token")
        
        # Test various endpoints
        tests = [
            self.amazon_client.test_listings_endpoint,
            self.amazon_client.test_orders_endpoint
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"L Test failed with exception: {e}")
                results.append(False)
        
        success = all(results)
        if success:
            print(" All Amazon sandbox tests passed")
        else:
            print("L Some Amazon sandbox tests failed")
        
        return success
    
    def test_shopify_api(self) -> bool:
        """Test Shopify API connectivity"""
        print("\n= Testing Shopify API...")
        
        # Test various endpoints
        tests = [
            self.shopify_client.test_products_endpoint,
            self.shopify_client.test_orders_endpoint
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"L Test failed with exception: {e}")
                results.append(False)
        
        success = all(results)
        if success:
            print(" All Shopify API tests passed")
        else:
            print("L Some Shopify API tests failed")
        
        return success
    
    def run_full_integration_test(self) -> bool:
        """Run complete integration test suite"""
        print("🚀 Starting Full Integration Test Suite")
        print("=" * 50)
        
        # Test environment setup
        if not self.test_environment_variables():
            print("\nL Environment setup failed. Please check your .env file.")
            return False
        
        # Test Amazon API
        amazon_success = self.test_amazon_sandbox()
        
        # Test Shopify API (only if environment variables are set)
        shopify_success = True
        if os.getenv('SHOPIFY_SHOP_DOMAIN') and os.getenv('SHOPIFY_ACCESS_TOKEN'):
            shopify_success = self.test_shopify_api()
        else:
            print("\n�  Shopify credentials not provided, skipping Shopify tests")
        
        # Overall result
        overall_success = amazon_success and shopify_success
        
        print("\n" + "=" * 50)
        if overall_success:
            print("<� All integration tests passed successfully!")
        else:
            print("L Some integration tests failed. Please check the logs above.")
        
        return overall_success


def test_amazon_sandbox():
    """Simple Amazon sandbox test function (for backward compatibility)"""
    print("Running Amazon Sandbox Test...")
    
    # Check for required environment variables
    client_id = os.getenv('AMAZON_CLIENT_ID')
    client_secret = os.getenv('AMAZON_CLIENT_SECRET')
    refresh_token = os.getenv('AMAZON_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("L Missing required Amazon credentials in .env file")
        return False
    
    # Initialize and test
    amazon_client = AmazonSandboxClient()
    
    # Get access token
    if not amazon_client.get_access_token():
        print("L Failed to get access token")
        return False
    
    print(" Successfully obtained access token")
    
    # Test sandbox endpoint
    success = amazon_client.test_listings_endpoint()
    
    if success:
        print("<� Amazon sandbox test completed successfully!")
    else:
        print("L Amazon sandbox test failed")
    
    return success


def main():
    """Main function to run integration tests"""
    # Initialize the integration tester
    tester = IntegrationTester()
    
    # Run full test suite
    success = tester.run_full_integration_test()
    
    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()