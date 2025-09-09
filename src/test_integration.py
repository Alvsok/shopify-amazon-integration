# -*- coding: utf-8 -*-
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
    """Amazon Selling Partner API Sandbox Client with detailed logging"""
    
    def __init__(self):
        self.client_id = os.getenv('AMAZON_CLIENT_ID')
        self.client_secret = os.getenv('AMAZON_CLIENT_SECRET')
        self.refresh_token = os.getenv('AMAZON_REFRESH_TOKEN')
        self.sandbox_url = "https://sandbox.sellingpartnerapi-na.amazon.com"
        self.token_url = "https://api.amazon.com/auth/o2/token"
        self.access_token = None
    
    def get_access_token(self) -> Optional[str]:
        """Get access token using refresh token"""
        print("🔑 Запрашиваем access token у Amazon...")
        print(f"   Client ID: {self.client_id[:20]}...")
        print(f"   Refresh Token: {self.refresh_token[:30] if self.refresh_token else 'НЕ НАЙДЕН'}...")
        
        try:
            token_data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(self.token_url, data=token_data)
            print(f"   Статус ответа: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ Ошибка получения токена: {response.text}")
                return None
                
            response.raise_for_status()
            
            token_response = response.json()
            self.access_token = token_response['access_token']
            
            expires_in = token_response.get('expires_in', 'неизвестно')
            token_type = token_response.get('token_type', 'Bearer')
            
            print(f"   ✅ Токен получен успешно!")
            print(f"   Тип токена: {token_type}")
            print(f"   Время действия: {expires_in} секунд")
            print(f"   Access token: {self.access_token[:50]}...")
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Ошибка сети при получении токена: {e}")
            return None
        except KeyError as e:
            print(f"   ❌ Отсутствует ключ в ответе: {e}")
            print(f"   Полный ответ: {response.text if 'response' in locals() else 'Нет ответа'}")
            return None
    
    def make_api_request(self, endpoint: str, method: str = 'GET', data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """Make authenticated API request to Amazon with proper headers"""
        if not self.access_token:
            print("⚠️  Access token отсутствует, получаем новый...")
            if not self.get_access_token():
                print("❌ Не удалось получить access token")
                return None
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-amz-access-token': self.access_token,
            'User-Agent': 'shopify-amazon-integration/1.0'
        }
        
        url = f"{self.sandbox_url}{endpoint}"
        
        print(f"📡 Отправляем запрос к Amazon API:")
        print(f"   URL: {url}")
        print(f"   Метод: {method}")
        print(f"   Заголовки: Authorization=Bearer ..., x-amz-access-token=...")
        if params:
            print(f"   Параметры: {params}")
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params)
            else:
                print(f"❌ Неподдерживаемый HTTP метод: {method}")
                return None
            
            print(f"📨 Получен ответ:")
            print(f"   Полный URL запроса: {response.url}")
            print(f"   Статус ответа: {response.status_code}")
            print(f"   Размер ответа: {len(response.content)} байт")
            
            if response.status_code == 200:
                print("   ✅ Запрос выполнен успешно!")
                try:
                    json_response = response.json()
                    print(f"   Структура ответа: {list(json_response.keys()) if isinstance(json_response, dict) else 'Не JSON объект'}")
                    return json_response
                except json.JSONDecodeError:
                    print("   ⚠️  Ответ не является валидным JSON")
                    print(f"   Содержимое: {response.text[:200]}...")
                    return None
            else:
                print(f"   ❌ API запрос завершился с ошибкой {response.status_code}")
                print(f"   Ответ сервера: {response.text}")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при выполнении запроса: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Ответ сервера: {e.response.text}")
            return None
    
    def test_marketplace_participation(self) -> bool:
        """
        Тест: Marketplace Participation API
        
        Что проверяем:
        - Доступ к информации о marketplace (торговых площадках)
        - На каких Amazon площадках зарегистрирован продавец
        - Статус участия в торговле
        - Базовую информацию о валюте и языке
        
        Это базовый тест для проверки, что API работает и продавец
        имеет доступ к Amazon marketplace.
        """
        print("🔍 Тестируем Amazon Marketplace Participation API")
        print("   📝 Что это: получаем информацию о торговых площадках Amazon")
        print("   🎯 Цель: проверить, на каких площадках зарегистрирован продавец")
        print("   📊 Ожидаемые данные: список площадок, валюты, статус участия")
        
        endpoint = "/sellers/v1/marketplaceParticipations"
        print(f"   🌐 Endpoint: {endpoint}")
        print("   📖 Документация: https://developer-docs.amazon.com/sp-api/docs/sellers-api-v1-reference")
        
        response = self.make_api_request(endpoint)
        
        if response is not None:
            print("✅ Marketplace Participation API - успешно!")
            
            # Детальный анализ ответа
            payload = response.get('payload', [])
            print(f"   📊 Найдено marketplace площадок: {len(payload)}")
            
            if len(payload) == 0:
                print("   ⚠️  Не найдено ни одной площадки - возможно, аккаунт не настроен")
                return True  # Техническиэ API работает
            
            for i, marketplace in enumerate(payload, 1):
                market = marketplace.get('marketplace', {})
                participation = marketplace.get('participation', {})
                store_name = marketplace.get('storeName', 'Не указано')
                
                print(f"   📦 Marketplace #{i}:")
                print(f"      🏪 Название магазина: {store_name}")
                print(f"      🌍 Площадка: {market.get('name', 'N/A')} ({market.get('id', 'N/A')})")
                print(f"      🇺🇸 Страна: {market.get('countryCode', 'N/A')}")
                print(f"      💰 Валюта: {market.get('defaultCurrencyCode', 'N/A')}")
                print(f"      🗣️  Язык: {market.get('defaultLanguageCode', 'N/A')}")
                print(f"      🌐 Домен: {market.get('domainName', 'N/A')}")
                print(f"      ✅ Участие в торговле: {'Да' if participation.get('isParticipating') else 'Нет'}")
                print(f"      ⚠️  Заблокированные товары: {'Да' if participation.get('hasSuspendedListings') else 'Нет'}")
                
                # Дополнительная информация для понимания
                if participation.get('isParticipating'):
                    print("      💡 Это означает: можно продавать товары на этой площадке")
                if participation.get('hasSuspendedListings'):
                    print("      ⚠️  Внимание: есть товары с ограничениями!")
                
            return True
        else:
            print("❌ Marketplace Participation API - ошибка!")
            print("   💡 Возможные причины:")
            print("      - Неверные credentials")
            print("      - Проблемы с доступом к API")
            print("      - Аккаунт не настроен для SP-API")
            return False
    
    def test_fba_inventory(self) -> bool:
        """
        Тест: FBA Inventory Summaries API
        
        Что проверяем:
        - Доступ к данным о товарах на складах Amazon (FBA - Fulfillment by Amazon)
        - Количество товаров в наличии
        - Статус товаров (доступные, зарезервированные, на пути и т.д.)
        - Информацию по конкретному marketplace
        
        FBA - это сервис Amazon, где они хранят и отправляют ваши товары.
        Этот API показывает, сколько товаров у вас лежит на их складах.
        """
        print("📦 Тестируем Amazon FBA Inventory API")
        print("   📝 Что это: получаем данные об инвентаре на складах Amazon")
        print("   🎯 Цель: узнать, сколько товаров лежит на складах FBA")
        print("   📊 Ожидаемые данные: список товаров, количества, статусы")
        print("   💡 FBA = Fulfillment by Amazon (склады и доставка через Amazon)")
        
        endpoint = "/fba/inventory/v1/summaries"
        params = {
            'granularityType': 'Marketplace',
            'granularityId': 'ATVPDKIKX0DER',
            'marketplaceIds': ['ATVPDKIKX0DER']
        }
        
        print(f"   🌐 Endpoint: {endpoint}")
        print("   📖 Документация: https://developer-docs.amazon.com/sp-api/docs/fba-inventory-api-v1-reference")
        print(f"   🔧 Параметры запроса:")
        print(f"      - Тип группировки: {params['granularityType']} (по площадке)")
        print(f"      - Marketplace ID: {params['granularityId']} (США - amazon.com)")
        print(f"      - Проверяемые площадки: {params['marketplaceIds']}")
        
        response = self.make_api_request(endpoint, params=params)
        
        if response is not None:
            print("✅ FBA Inventory API - успешно!")
            
            # Детальный анализ ответа
            payload = response.get('payload', {})
            granularity = payload.get('granularity', {})
            inventory_summaries = payload.get('inventorySummaries', [])
            
            print(f"   📊 Информация о запросе:")
            print(f"      - Группировка: {granularity.get('granularityType', 'N/A')}")
            print(f"      - Marketplace: {granularity.get('granularityId', 'N/A')}")
            
            print(f"   📦 Найдено товаров в инвентаре: {len(inventory_summaries)}")
            
            if len(inventory_summaries) == 0:
                print("   ℹ️  В sandbox режиме инвентарь пустой - это нормально")
                print("   ℹ️  В реальном аккаунте здесь будут ваши товары на складах Amazon")
                print("   💡 Что здесь было бы в продакшене:")
                print("      - ASIN коды товаров")
                print("      - Количества на складах") 
                print("      - Статусы товаров (доступно, зарезервировано, на пути)")
                print("      - SKU коды продавца")
                print("      - Названия товаров")
            else:
                for i, item in enumerate(inventory_summaries, 1):
                    print(f"   📦 Товар #{i}:")
                    print(f"      - ASIN: {item.get('asin', 'N/A')} (Amazon уникальный ID)")
                    print(f"      - FNSKU: {item.get('fnSku', 'N/A')} (Fulfillment Network SKU)")
                    print(f"      - Селлер SKU: {item.get('sellerSku', 'N/A')} (ваш артикул)")
                    print(f"      - Название: {item.get('productName', 'N/A')}")
                    
                    total_quantity = item.get('totalQuantity', 0)
                    print(f"      - Общее количество: {total_quantity} шт.")
                    
                    if 'inventoryDetails' in item:
                        details = item['inventoryDetails']
                        print(f"      - Детали инвентаря:")
                        fulfillable = details.get('fulfillableQuantity', 0)
                        inbound = details.get('inboundWorkingQuantity', 0) 
                        inbound_shipped = details.get('inboundShippedQuantity', 0)
                        reserved = details.get('reservedQuantity', 0)
                        
                        print(f"        * Доступно для продажи: {fulfillable} шт.")
                        print(f"        * В пути (обработка): {inbound} шт.")
                        print(f"        * В пути (отправлено): {inbound_shipped} шт.")
                        print(f"        * Зарезервировано: {reserved} шт.")
                        
                        if fulfillable > 0:
                            print(f"        ✅ Товар доступен для продажи!")
                        else:
                            print(f"        ⚠️  Товар недоступен для продажи")
                
            print("   💡 Что означает этот тест:")
            print("      - API работает и может получать данные об инвентаре")
            print("      - Подключение к FBA системе Amazon функционирует")
            print("      - В продакшене здесь будет информация о ваших товарах")
                
            return True
        else:
            print("❌ FBA Inventory API - ошибка!")
            print("   💡 Возможные причины:")
            print("      - Неверные параметры запроса")
            print("      - Нет доступа к FBA API")
            print("      - Аккаунт не настроен для работы с FBA")
            return False


class ShopifyClient:
    """Shopify API Client with detailed logging"""
    
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
                print(f"Неподдерживаемый HTTP метод: {method}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Shopify API запрос завершился с ошибкой: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Ответ сервера: {e.response.text}")
            return None
    
    def test_products_endpoint(self) -> bool:
        """Test the products endpoint with detailed logging"""
        print("🛍️  Тестируем Shopify Products API")
        print("   📝 Что это: получаем список товаров из Shopify магазина")
        
        endpoint = "/products.json?limit=5"
        response = self.make_api_request(endpoint)
        
        if response is not None:
            products = response.get('products', [])
            print(f"✅ Products endpoint test successful")
            print(f"   📦 Найдено товаров: {len(products)}")
            
            for i, product in enumerate(products, 1):
                print(f"   🛍️  Товар #{i}: {product.get('title', 'Без названия')}")
                print(f"      - ID: {product.get('id')}")
                print(f"      - Статус: {product.get('status', 'unknown')}")
                print(f"      - Вариантов: {len(product.get('variants', []))}")
            
            return True
        else:
            print("❌ Products endpoint test failed")
            return False
    
    def test_orders_endpoint(self) -> bool:
        """Test the orders endpoint with detailed logging"""
        print("📋 Тестируем Shopify Orders API")
        print("   📝 Что это: получаем список заказов из Shopify магазина")
        
        endpoint = "/orders.json?limit=5"
        response = self.make_api_request(endpoint)
        
        if response is not None:
            orders = response.get('orders', [])
            print(f"✅ Orders endpoint test successful")
            print(f"   📋 Найдено заказов: {len(orders)}")
            
            if len(orders) == 0:
                print("   ℹ️  Заказов нет - нормально для тестового магазина")
            else:
                for i, order in enumerate(orders, 1):
                    print(f"   📋 Заказ #{i}: #{order.get('order_number', order.get('id'))}")
                    print(f"      - Сумма: {order.get('total_price', '0')} {order.get('currency', 'USD')}")
                    print(f"      - Статус: {order.get('financial_status', 'unknown')}")
                    print(f"      - Товаров: {len(order.get('line_items', []))}")
            
            return True
        else:
            print("❌ Orders endpoint test failed")
            return False


class IntegrationTester:
    """Main integration tester class with detailed explanations"""
    
    def __init__(self):
        self.amazon_client = AmazonSandboxClient()
        self.shopify_client = ShopifyClient()
    
    def test_environment_variables(self) -> bool:
        """Test if all required environment variables are set"""
        print("🔧 Проверяем переменные окружения...")
        print("   📁 Файл: .env")
        
        required_vars = [
            'AMAZON_CLIENT_ID',
            'AMAZON_CLIENT_SECRET', 
            'AMAZON_REFRESH_TOKEN',
            'SHOPIFY_SHOP_DOMAIN',
            'SHOPIFY_ACCESS_TOKEN'
        ]
        
        missing_vars = []
        found_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                found_vars.append(var)
                # Показываем первые символы для проверки
                if 'TOKEN' in var or 'SECRET' in var:
                    display_value = f"{value[:15]}..." if len(value) > 15 else value
                else:
                    display_value = value
                print(f"   ✅ {var}: {display_value}")
        
        if missing_vars:
            print(f"   ❌ Отсутствуют переменные: {', '.join(missing_vars)}")
            print("   💡 Проверьте файл .env и добавьте недостающие переменные")
            return False
        else:
            print("   ✅ Все переменные окружения настроены")
            return True
    
    def test_amazon_sandbox(self) -> bool:
        """Test Amazon Sandbox API connectivity with detailed explanations"""
        print("\\n🔄 Тестируем Amazon Sandbox API...")
        print("=" * 60)
        print("📖 О Amazon SP-API Sandbox:")
        print("   - Тестовая среда для разработки интеграций")
        print("   - Имитирует реальный Amazon Selling Partner API")
        print("   - Безопасно для тестирования без влияния на продажи")
        print("   - Возвращает фиктивные данные, похожие на реальные")
        print("=" * 60)
        
        # Test token generation
        print("\\n🔐 Этап 1: Проверка авторизации")
        if not self.amazon_client.get_access_token():
            print("❌ Не удалось получить Amazon access token")
            print("💡 Проверьте credentials в .env файле")
            return False
        
        print("✅ Авторизация успешна!")
        
        # Test various endpoints
        print("\\n🧪 Этап 2: Тестирование API endpoints")
        tests = [
            ("Marketplace Participation", self.amazon_client.test_marketplace_participation),
            ("FBA Inventory", self.amazon_client.test_fba_inventory)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\\n--- {test_name} ---")
            try:
                result = test_func()
                results.append(result)
                if result:
                    print(f"✅ {test_name} - прошел успешно")
                else:
                    print(f"❌ {test_name} - завершился с ошибкой")
            except Exception as e:
                print(f"❌ {test_name} - исключение: {e}")
                results.append(False)
        
        success = all(results)
        
        print("\\n" + "=" * 60)
        if success:
            print("🎉 Все Amazon sandbox тесты прошли успешно!")
            print("💡 Это означает:")
            print("   - Ваши Amazon credentials работают") 
            print("   - API подключение настроено правильно")
            print("   - Можно переходить к разработке реальной интеграции")
        else:
            print("⚠️  Некоторые Amazon sandbox тесты завершились с ошибками")
            print("💡 Возможные решения:")
            print("   - Проверьте credentials в Amazon Developer Console")
            print("   - Убедитесь, что приложение активно")
            print("   - Проверьте настройки sandbox")
        
        return success
    
    def test_shopify_api(self) -> bool:
        """Test Shopify API connectivity"""
        print("\\n🔄 Тестируем Shopify API...")
        print("=" * 60)
        print("📖 О Shopify API:")
        print("   - Реальный API вашего Shopify магазина")
        print("   - Доступ к товарам, заказам, клиентам и другим данным")
        print("   - Требует настройки Private App или Custom App")
        print("=" * 60)
        
        # Test various endpoints
        tests = [
            ("Products API", self.shopify_client.test_products_endpoint),
            ("Orders API", self.shopify_client.test_orders_endpoint)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\\n--- {test_name} ---")
            try:
                result = test_func()
                results.append(result)
            except Exception as e:
                print(f"❌ {test_name} завершился с исключением: {e}")
                results.append(False)
        
        success = all(results)
        
        print("\\n" + "=" * 60) 
        if success:
            print("✅ Все Shopify API тесты прошли успешно!")
        else:
            print("❌ Некоторые Shopify API тесты завершились с ошибками")
        
        return success
    
    def run_full_integration_test(self) -> bool:
        """Run complete integration test suite with detailed explanations"""
        print("🚀 Запуск полного интеграционного теста")
        print("=" * 60)
        print("📋 План тестирования:")
        print("   1. Проверка переменных окружения")
        print("   2. Тест Amazon SP-API Sandbox")
        print("   3. Тест Shopify API")
        print("   4. Общее заключение")
        print("=" * 60)
        
        # Test environment setup
        print("\\n📋 Шаг 1: Проверка окружения")
        if not self.test_environment_variables():
            print("\\n❌ Настройка окружения завершилась с ошибками")
            print("💡 Исправьте ошибки в .env файле перед продолжением")
            return False
        
        # Test Amazon API
        amazon_success = self.test_amazon_sandbox()
        
        # Test Shopify API (only if environment variables are set)
        shopify_success = True
        if os.getenv('SHOPIFY_SHOP_DOMAIN') and os.getenv('SHOPIFY_ACCESS_TOKEN'):
            shopify_success = self.test_shopify_api()
        else:
            print("\\n⚠️  Shopify credentials не предоставлены, пропускаем Shopify тесты")
        
        # Overall result
        overall_success = amazon_success and shopify_success
        
        print("\\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        
        print(f"🔧 Окружение: ✅ Настроено")
        print(f"🚀 Amazon SP-API: {'✅ Работает' if amazon_success else '❌ Ошибки'}")
        print(f"🛍️  Shopify API: {'✅ Работает' if shopify_success else '❌ Ошибки'}")
        
        if overall_success:
            print("\\n🎉 Все интеграционные тесты прошли успешно!")
            print("\\n🚀 Следующие шаги:")
            print("   1. Интеграция готова к разработке")
            print("   2. Можете создавать функции синхронизации")  
            print("   3. Настройте обработку вебхуков")
            print("   4. Реализуйте бизнес-логику интеграции")
        else:
            print("\\n⚠️  Некоторые интеграционные тесты завершились с ошибками")
            print("\\n🔧 Рекомендации:")
            if not amazon_success:
                print("   - Исправьте проблемы с Amazon API")
            if not shopify_success:
                print("   - Исправьте проблемы с Shopify API")
            print("   - Повторите тесты после исправлений")
        
        print("=" * 60)
        
        return overall_success


def test_amazon_sandbox():
    """Simple Amazon sandbox test function (for backward compatibility)"""
    print("🧪 Запуск упрощенного Amazon Sandbox теста...")
    
    # Check for required environment variables
    client_id = os.getenv('AMAZON_CLIENT_ID')
    client_secret = os.getenv('AMAZON_CLIENT_SECRET') 
    refresh_token = os.getenv('AMAZON_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Отсутствуют обязательные Amazon credentials в .env файле")
        print("💡 Проверьте наличие: AMAZON_CLIENT_ID, AMAZON_CLIENT_SECRET, AMAZON_REFRESH_TOKEN")
        return False
    
    # Initialize and test
    amazon_client = AmazonSandboxClient()
    
    # Get access token
    if not amazon_client.get_access_token():
        print("❌ Не удалось получить access token")
        return False
    
    print("✅ Access token получен успешно")
    
    # Test sandbox endpoint
    success = amazon_client.test_marketplace_participation()
    
    if success:
        print("🎉 Amazon sandbox тест завершен успешно!")
    else:
        print("❌ Amazon sandbox тест завершился с ошибкой")
    
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