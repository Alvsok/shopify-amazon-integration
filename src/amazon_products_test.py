# -*- coding: utf-8 -*-
"""
Специализированный тест для поиска товаров в Amazon Sandbox
Тестирует ВСЕ возможные способы получения списка товаров Amazon
"""
import os
import json
import datetime
from test_integration import AmazonSandboxClient
from dotenv import load_dotenv

# Загружаем .env из корневой директории проекта
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class AmazonProductsFinder:
    def __init__(self):
        self.client = AmazonSandboxClient()
        self.found_products = []
        self.working_endpoints = []
        self.failed_endpoints = []

    def authenticate(self):
        """Получаем токен авторизации"""
        print("🔐 АВТОРИЗАЦИЯ В AMAZON SP-API")
        print("=" * 50)
        
        if not self.client.get_access_token():
            print("❌ Не удалось получить токен - тест остановлен")
            return False
            
        print("✅ Авторизация успешна!\n")
        return True

    def test_catalog_search_variations(self):
        """Тестируем разные варианты поиска в каталоге"""
        print("🔍 ТЕСТ 1: Поиск товаров в каталоге Amazon")
        print("=" * 50)
        
        # Разные версии Catalog API
        catalog_tests = [
            {
                'name': 'Catalog 2022 - Simple Search',
                'endpoint': '/catalog/2022-04-01/items',
                'params': {'keywords': 'book', 'marketplaceIds': 'ATVPDKIKX0DER'}
            },
            {
                'name': 'Catalog 2022 - Electronics',
                'endpoint': '/catalog/2022-04-01/items',
                'params': {'keywords': 'phone', 'marketplaceIds': 'ATVPDKIKX0DER'}
            },
            {
                'name': 'Catalog 2022 - Minimal Params',
                'endpoint': '/catalog/2022-04-01/items',
                'params': {'marketplaceIds': 'ATVPDKIKX0DER'}
            },
            {
                'name': 'Catalog 2020 - Legacy API',
                'endpoint': '/catalog/v0/items',
                'params': {'Query': 'book', 'MarketplaceId': 'ATVPDKIKX0DER'}
            },
            {
                'name': 'Catalog by ASIN - Test ASIN',
                'endpoint': '/catalog/2022-04-01/items/B08N5WRWNW',
                'params': {'marketplaceIds': 'ATVPDKIKX0DER', 'includedData': 'summaries'}
            },
            {
                'name': 'Catalog by ASIN - Another Test',
                'endpoint': '/catalog/2022-04-01/items/B07VGRJDFY',
                'params': {'marketplaceIds': 'ATVPDKIKX0DER'}
            }
        ]
        
        for test in catalog_tests:
            print(f"\n🧪 {test['name']}")
            print(f"   📍 Endpoint: {test['endpoint']}")
            print(f"   🔧 Параметры: {test['params']}")
            
            response = self.client.make_api_request(test['endpoint'], params=test['params'])
            
            if response and response.get('items'):
                items = response['items']
                print(f"   ✅ Найдено товаров: {len(items)}")
                self.working_endpoints.append(test['name'])
                
                # Показываем первые товары
                for i, item in enumerate(items[:3]):
                    asin = item.get('asin', 'N/A')
                    summaries = item.get('summaries', [])
                    title = summaries[0].get('itemName', 'Без названия') if summaries else 'Без названия'
                    print(f"      📦 {i+1}. ASIN: {asin} - {title}")
                    
                self.found_products.extend(items[:5])  # Сохраняем первые 5
                
            elif response and 'asin' in response:  # Одиночный товар
                print(f"   ✅ Найден товар: {response.get('asin')}")
                summaries = response.get('summaries', [])
                if summaries:
                    title = summaries[0].get('itemName', 'Без названия')
                    print(f"   📝 Название: {title}")
                self.working_endpoints.append(test['name'])
                self.found_products.append(response)
                
            else:
                print(f"   ❌ Ошибка или товары не найдены")
                self.failed_endpoints.append(test['name'])

    def test_listings_variations(self):
        """Тестируем разные способы получения листингов продавца"""
        print("\n📋 ТЕСТ 2: Получение листингов продавца")
        print("=" * 50)
        
        # Разные подходы к листингам
        listings_tests = [
            {
                'name': 'Listings 2021 - All Items',
                'endpoint': '/listings/2021-08-01/items',
                'params': {'sellerId': 'A2EUQ1WTGCTBG2', 'marketplaceIds': 'ATVPDKIKX0DER'}
            },
            {
                'name': 'Listings 2021 - Without Seller ID',
                'endpoint': '/listings/2021-08-01/items',
                'params': {'marketplaceIds': 'ATVPDKIKX0DER'}
            },
            {
                'name': 'Listings 2020 - Legacy',
                'endpoint': '/listings/2020-09-01/items',
                'params': {'sellerId': 'A2EUQ1WTGCTBG2', 'marketplaceIds': 'ATVPDKIKX0DER'}
            },
            {
                'name': 'Merchant Listings',
                'endpoint': '/mfn/v0/eligibleShippingServices',
                'params': {'marketplaceIds': ['ATVPDKIKX0DER']}
            }
        ]
        
        for test in listings_tests:
            print(f"\n🧪 {test['name']}")
            print(f"   📍 Endpoint: {test['endpoint']}")
            
            response = self.client.make_api_request(test['endpoint'], params=test['params'])
            
            if response:
                if 'items' in response and response['items']:
                    items = response['items']
                    print(f"   ✅ Найдено листингов: {len(items)}")
                    self.working_endpoints.append(test['name'])
                    
                    for i, item in enumerate(items[:3]):
                        sku = item.get('sku', 'N/A')
                        asin = item.get('asin', 'N/A')
                        print(f"      📦 {i+1}. SKU: {sku}, ASIN: {asin}")
                        
                else:
                    print(f"   ℹ️  API отвечает, но листингов нет (нормально для sandbox)")
                    self.working_endpoints.append(test['name'])
            else:
                print(f"   ❌ Ошибка доступа")
                self.failed_endpoints.append(test['name'])

    def test_orders_for_products(self):
        """Тестируем Orders API для получения информации о товарах через заказы"""
        print("\n📊 ТЕСТ 3: Поиск товаров через Orders API")
        print("=" * 50)
        
        # Разные временные периоды для поиска заказов
        now = datetime.datetime.now()
        periods = [
            ('1 день назад', now - datetime.timedelta(days=1)),
            ('1 неделя назад', now - datetime.timedelta(days=7)),
            ('1 месяц назад', now - datetime.timedelta(days=30)),
            ('6 месяцев назад', now - datetime.timedelta(days=180)),
            ('1 год назад', now - datetime.timedelta(days=365))
        ]
        
        for period_name, start_date in periods:
            print(f"\n🧪 Поиск заказов: {period_name}")
            
            orders_params = {
                'MarketplaceIds': ['ATVPDKIKX0DER'],
                'CreatedAfter': start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            print(f"   📅 С даты: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            response = self.client.make_api_request('/orders/v0/orders', params=orders_params)
            
            if response and response.get('payload', {}).get('Orders'):
                orders = response['payload']['Orders']
                print(f"   ✅ Найдено заказов: {len(orders)}")
                self.working_endpoints.append(f"Orders - {period_name}")
                
                # Извлекаем товары из заказов
                for order in orders[:3]:  # Первые 3 заказа
                    order_id = order.get('AmazonOrderId', 'N/A')
                    print(f"   📋 Заказ: {order_id}")
                    
                    # Получаем товары заказа
                    items_response = self.client.make_api_request(
                        f'/orders/v0/orders/{order_id}/orderItems'
                    )
                    
                    if items_response and items_response.get('payload', {}).get('OrderItems'):
                        items = items_response['payload']['OrderItems']
                        print(f"      📦 Товаров в заказе: {len(items)}")
                        
                        for item in items[:2]:  # Первые 2 товара
                            asin = item.get('ASIN', 'N/A')
                            title = item.get('Title', 'Без названия')
                            sku = item.get('SellerSKU', 'N/A')
                            print(f"         - ASIN: {asin}, SKU: {sku}")
                            print(f"         - Товар: {title}")
                break  # Если нашли заказы, прерываем поиск по другим периодам
            else:
                print(f"   ❌ Заказов не найдено")
                self.failed_endpoints.append(f"Orders - {period_name}")

    def test_inventory_variations(self):
        """Тестируем разные inventory API"""
        print("\n📦 ТЕСТ 4: Поиск товаров через Inventory APIs")
        print("=" * 50)
        
        inventory_tests = [
            {
                'name': 'FBA Inventory v1',
                'endpoint': '/fba/inventory/v1/summaries',
                'params': {
                    'granularityType': 'Marketplace',
                    'granularityId': 'ATVPDKIKX0DER',
                    'marketplaceIds': ['ATVPDKIKX0DER']
                }
            },
            {
                'name': 'MFN Inventory',
                'endpoint': '/inventory/v1/summaries',
                'params': {'granularityType': 'Marketplace', 'granularityId': 'ATVPDKIKX0DER'}
            },
            {
                'name': 'Inventory Details',
                'endpoint': '/fba/inventory/v1/summaries',
                'params': {
                    'details': True,
                    'granularityType': 'Marketplace', 
                    'granularityId': 'ATVPDKIKX0DER'
                }
            }
        ]
        
        for test in inventory_tests:
            print(f"\n🧪 {test['name']}")
            print(f"   📍 Endpoint: {test['endpoint']}")
            
            response = self.client.make_api_request(test['endpoint'], params=test['params'])
            
            if response and response.get('payload', {}).get('inventorySummaries'):
                items = response['payload']['inventorySummaries']
                if items:
                    print(f"   ✅ Найдено товаров в инвентаре: {len(items)}")
                    self.working_endpoints.append(test['name'])
                    
                    for i, item in enumerate(items[:3]):
                        asin = item.get('asin', 'N/A')
                        sku = item.get('sellerSku', 'N/A')
                        quantity = item.get('totalQuantity', 0)
                        print(f"      📦 {i+1}. ASIN: {asin}, SKU: {sku}, Количество: {quantity}")
                else:
                    print(f"   ℹ️  Inventory API работает, но товаров нет")
                    self.working_endpoints.append(test['name'])
            else:
                print(f"   ❌ Ошибка или недоступен")
                self.failed_endpoints.append(test['name'])

    def test_reports_api(self):
        """Тестируем Reports API для получения данных о товарах"""
        print("\n📈 ТЕСТ 5: Поиск товаров через Reports API")
        print("=" * 50)
        
        reports_tests = [
            {
                'name': 'Inventory Report',
                'reportType': 'GET_MERCHANT_LISTINGS_ALL_DATA',
                'description': 'Отчет по всем листингам продавца'
            },
            {
                'name': 'FBA Inventory Report',
                'reportType': 'GET_FBA_INVENTORY_AGED_REPORT',
                'description': 'Отчет по FBA инвентарю'
            },
            {
                'name': 'Active Listings Report',
                'reportType': 'GET_MERCHANT_LISTINGS_DATA',
                'description': 'Активные листинги'
            }
        ]
        
        for test in reports_tests:
            print(f"\n🧪 {test['name']} - {test['description']}")
            
            # Создаем отчет
            create_params = {
                'reportType': test['reportType'],
                'marketplaceIds': ['ATVPDKIKX0DER']
            }
            
            response = self.client.make_api_request('/reports/2021-06-30/reports', 
                                                 method='POST', data=create_params)
            
            if response and response.get('reportId'):
                report_id = response['reportId']
                print(f"   ✅ Отчет создан: {report_id}")
                print(f"   ℹ️  В продакшене нужно ждать готовности отчета")
                self.working_endpoints.append(test['name'])
            else:
                print(f"   ❌ Не удалось создать отчет")
                self.failed_endpoints.append(test['name'])

    def test_feeds_api(self):
        """Тестируем Feeds API"""
        print("\n📤 ТЕСТ 6: Feeds API (загрузка товаров)")
        print("=" * 50)
        
        # Проверяем доступные типы фидов
        response = self.client.make_api_request('/feeds/2021-06-30/documents')
        
        if response:
            print("   ✅ Feeds API доступен")
            print("   💡 Этот API используется для загрузки товаров в Amazon")
            self.working_endpoints.append("Feeds API")
        else:
            print("   ❌ Feeds API недоступен")
            self.failed_endpoints.append("Feeds API")

    def show_summary(self):
        """Показываем итоговый отчет"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ: ПОИСК ТОВАРОВ AMAZON")
        print("=" * 60)
        
        print(f"\n✅ РАБОТАЮЩИЕ API ({len(self.working_endpoints)}):")
        for endpoint in self.working_endpoints:
            print(f"   ✅ {endpoint}")
        
        print(f"\n❌ НЕ РАБОТАЮЩИЕ API ({len(self.failed_endpoints)}):")
        for endpoint in self.failed_endpoints:
            print(f"   ❌ {endpoint}")
        
        print(f"\n📦 НАЙДЕНО ТОВАРОВ: {len(self.found_products)}")
        
        if self.found_products:
            print("\n🔍 ДЕТАЛИ НАЙДЕННЫХ ТОВАРОВ:")
            for i, product in enumerate(self.found_products[:5], 1):
                asin = product.get('asin', 'N/A')
                print(f"\n   📦 Товар #{i}:")
                print(f"      🏷️  ASIN: {asin}")
                
                summaries = product.get('summaries', [])
                if summaries:
                    summary = summaries[0]
                    title = summary.get('itemName', 'Без названия')
                    brand = summary.get('brand', 'Без бренда')
                    print(f"      📝 Название: {title}")
                    print(f"      🏢 Бренд: {brand}")
                
                identifiers = product.get('identifiers', {})
                if identifiers:
                    upc = identifiers.get('upcCodes', [])
                    if upc:
                        print(f"      🔢 UPC: {upc[0]}")
        else:
            print("   ℹ️  В sandbox режиме товары обычно не доступны")
        
        print("\n💡 ВЫВОДЫ:")
        print("=" * 30)
        
        if len(self.working_endpoints) > len(self.failed_endpoints):
            print("✅ Amazon SP-API в основном функционирует!")
        else:
            print("⚠️  Многие Amazon API недоступны в sandbox")
        
        print("\n🚀 РЕКОМЕНДАЦИИ:")
        print("   1. Sandbox ограничен - многие API работают только в production")
        print("   2. Для реальной интеграции используйте production credentials")
        print("   3. Работающие API показывают, что подключение настроено правильно")
        print("   4. Можно переходить к разработке функций синхронизации")

def main():
    """Главная функция теста"""
    print("🔍 AMAZON PRODUCTS FINDER - Специализированный тест поиска товаров")
    print("🎯 Цель: Найти товары Amazon всеми возможными способами")
    print("=" * 70)
    
    finder = AmazonProductsFinder()
    
    # Авторизация
    if not finder.authenticate():
        return
    
    # Выполняем все тесты
    finder.test_catalog_search_variations()
    finder.test_listings_variations()
    finder.test_orders_for_products()
    finder.test_inventory_variations()
    finder.test_reports_api()
    finder.test_feeds_api()
    
    # Показываем итоги
    finder.show_summary()

if __name__ == "__main__":
    main()