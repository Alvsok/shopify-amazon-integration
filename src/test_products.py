# -*- coding: utf-8 -*-
import os
from test_integration import AmazonSandboxClient, ShopifyClient
from dotenv import load_dotenv

# Загружаем .env из корневой директории проекта  
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def test_amazon_products():
    """Специальный тест для получения данных о товарах Amazon"""
    print("🔍 ТЕСТ: Поиск товаров в Amazon Sandbox")
    print("=" * 60)
    
    client = AmazonSandboxClient()
    
    # Получаем токен
    if not client.get_access_token():
        print("❌ Не удалось получить токен")
        return
    
    print("\n📦 1. Информация о магазине:")
    print("-" * 40)
    
    # 1. Сначала получим информацию о магазине
    marketplace_response = client.make_api_request("/sellers/v1/marketplaceParticipations")
    if marketplace_response:
        payload = marketplace_response.get('payload', [])
        if payload:
            store = payload[0]
            market = store.get('marketplace', {})
            print(f"🏪 Магазин: {store.get('storeName', 'N/A')}")
            print(f"🌍 Площадка: {market.get('name', 'N/A')} ({market.get('id', 'N/A')})")
            print(f"💰 Валюта: {market.get('defaultCurrencyCode', 'N/A')}")
            print(f"🌐 Домен: {market.get('domainName', 'N/A')}")
    
    print("\n📋 2. Попробуем разные способы получения товаров:")
    print("-" * 50)
    
    # 2. Попробуем Catalog API с разными параметрами
    catalog_endpoints = [
        {
            'name': 'Catalog Simple Search',
            'endpoint': '/catalog/2022-04-01/items',
            'params': {
                'keywords': 'book',
                'marketplaceIds': 'ATVPDKIKX0DER'
            }
        },
        {
            'name': 'Catalog by ASIN',
            'endpoint': '/catalog/2022-04-01/items/B08N5WRWNW',  # Пример ASIN
            'params': {
                'marketplaceIds': 'ATVPDKIKX0DER',
                'includedData': 'summaries'
            }
        }
    ]
    
    for test in catalog_endpoints:
        print(f"\n🧪 Тестируем: {test['name']}")
        print(f"   Endpoint: {test['endpoint']}")
        print(f"   Параметры: {test['params']}")
        
        response = client.make_api_request(test['endpoint'], params=test['params'])
        if response:
            print("   ✅ Успешный ответ!")
            if 'items' in response:
                items = response['items']
                print(f"   📦 Найдено товаров: {len(items)}")
                for i, item in enumerate(items[:3]):  # Показываем первые 3
                    print(f"      {i+1}. ASIN: {item.get('asin', 'N/A')}")
            elif 'asin' in response:  # Одиночный товар
                print(f"   📦 ASIN: {response.get('asin', 'N/A')}")
                summaries = response.get('summaries', [])
                if summaries:
                    summary = summaries[0]
                    print(f"   📝 Название: {summary.get('itemName', 'N/A')}")
                    print(f"   🏢 Бренд: {summary.get('brand', 'N/A')}")
        else:
            print("   ❌ Ошибка или нет доступа")
    
    print("\n📊 3. Попробуем Orders API:")
    print("-" * 30)
    
    # 3. Orders API с правильными параметрами
    import datetime
    
    # Дата год назад
    year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    orders_params = {
        'MarketplaceIds': ['ATVPDKIKX0DER'],
        'CreatedAfter': year_ago,
        'OrderStatuses': ['Pending', 'Unshipped', 'Shipped']
    }
    
    print(f"🧪 Тестируем Orders API")
    print(f"   Параметры: {orders_params}")
    
    orders_response = client.make_api_request('/orders/v0/orders', params=orders_params)
    if orders_response:
        orders = orders_response.get('payload', {}).get('Orders', [])
        print(f"   📋 Найдено заказов: {len(orders)}")
        for i, order in enumerate(orders[:5]):  # Первые 5
            print(f"      {i+1}. Order ID: {order.get('AmazonOrderId', 'N/A')}")
            print(f"         Статус: {order.get('OrderStatus', 'N/A')}")
            print(f"         Сумма: {order.get('OrderTotal', {}).get('Amount', 'N/A')} {order.get('OrderTotal', {}).get('CurrencyCode', 'USD')}")
    else:
        print("   ❌ Orders API недоступен в sandbox или нет заказов")

def compare_shopify_amazon():
    """Сравниваем товары Shopify с возможностями Amazon"""
    print("\n" + "=" * 60)
    print("🔄 СРАВНЕНИЕ: Товары Shopify vs Возможности Amazon")
    print("=" * 60)
    
    # Shopify товары
    shopify = ShopifyClient()
    shopify_response = shopify.make_api_request('/products.json?limit=5')
    
    if shopify_response:
        products = shopify_response.get('products', [])
        print(f"\n🛍️  Shopify товары ({len(products)} шт.):")
        print("-" * 40)
        
        for i, product in enumerate(products, 1):
            title = product.get('title', 'Без названия')
            product_id = product.get('id')
            variants = product.get('variants', [])
            
            print(f"{i}. 📦 {title}")
            print(f"   ID: {product_id}")
            print(f"   Вариантов: {len(variants)}")
            
            if variants:
                variant = variants[0]
                price = variant.get('price', 'N/A')
                sku = variant.get('sku', 'N/A')
                inventory = variant.get('inventory_quantity', 0)
                
                print(f"   💰 Цена: ${price}")
                print(f"   🏷️  SKU: {sku}")
                print(f"   📊 Остаток: {inventory} шт.")
            
            print()
    
    print("💡 ВОЗМОЖНОСТИ ИНТЕГРАЦИИ:")
    print("-" * 30)
    print("✅ Что РАБОТАЕТ сейчас:")
    print("   - Получение данных о marketplace Amazon")
    print("   - Проверка статуса продавца")  
    print("   - Доступ к FBA inventory API")
    print("   - Полный доступ к Shopify товарам")
    
    print("\n🚀 Что можно РАЗРАБОТАТЬ:")
    print("   - Синхронизация Shopify → Amazon")
    print("   - Обновление цен и остатков")
    print("   - Создание листингов на Amazon")
    print("   - Управление заказами")
    
    print("\n⚠️  ОГРАНИЧЕНИЯ Sandbox:")
    print("   - Каталог товаров ограничен")
    print("   - Нет реальных листингов продавца")
    print("   - Заказы могут отсутствовать")
    print("   - Некоторые API требуют production")

if __name__ == "__main__":
    test_amazon_products()
    compare_shopify_amazon()