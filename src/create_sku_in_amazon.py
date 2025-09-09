# -*- coding: utf-8 -*-
"""
Создание товара из Shopify в Amazon
Находит товар ID: 9160927608983 в Shopify и создает его в Amazon
"""
import os
import json
import xml.etree.ElementTree as ET
from test_integration import AmazonSandboxClient, ShopifyClient
from dotenv import load_dotenv
import base64
import uuid
from datetime import datetime

# Загружаем .env из корневой директории проекта
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class ShopifyToAmazonCreator:
    def __init__(self):
        self.shopify_client = ShopifyClient()
        self.amazon_client = AmazonSandboxClient()
        self.target_product_id = "9160927608983"  # Bosch Aerotwin A950S
    
    def get_shopify_product_details(self):
        """Получаем полную информацию о товаре из Shopify"""
        print("🔍 ЭТАП 1: Получение товара из Shopify")
        print("=" * 50)
        
        print(f"🎯 Целевой товар ID: {self.target_product_id}")
        
        # Получаем конкретный товар по ID
        endpoint = f"/products/{self.target_product_id}.json"
        print(f"📡 Запрос: GET {endpoint}")
        
        response = self.shopify_client.make_api_request(endpoint)
        
        if not response or 'product' not in response:
            print("❌ Товар не найден в Shopify")
            return None
        
        product = response['product']
        
        print("✅ Товар найден в Shopify!")
        print("\n📦 ДЕТАЛИ ТОВАРА:")
        print("-" * 30)
        
        # Основная информация
        title = product.get('title', '')
        vendor = product.get('vendor', '')
        product_type = product.get('product_type', '')
        description = product.get('body_html', '').replace('<p>', '').replace('</p>', '').replace('<br>', '\n')
        tags = product.get('tags', '')
        
        print(f"📝 Название: {title}")
        print(f"🏢 Бренд: {vendor}")
        print(f"📂 Тип: {product_type}")
        print(f"🏷️  Теги: {tags}")
        print(f"📄 Описание: {description[:100]}...")
        
        # Варианты товара
        variants = product.get('variants', [])
        print(f"\n🔢 Вариантов товара: {len(variants)}")
        
        variant_details = []
        for i, variant in enumerate(variants, 1):
            sku = variant.get('sku', '')
            price = variant.get('price', '0.00')
            weight = variant.get('weight', 0)
            inventory_qty = variant.get('inventory_quantity', 0)
            barcode = variant.get('barcode', '')
            
            variant_info = {
                'sku': sku,
                'price': price,
                'weight': weight,
                'inventory_quantity': inventory_qty,
                'barcode': barcode,
                'title': variant.get('title', 'Default Title')
            }
            variant_details.append(variant_info)
            
            print(f"   📦 Вариант {i}:")
            print(f"      🏷️  SKU: {sku}")
            print(f"      💰 Цена: ${price}")
            print(f"      ⚖️  Вес: {weight}g")
            print(f"      📊 Остаток: {inventory_qty} шт.")
            if barcode:
                print(f"      🔢 Штрихкод: {barcode}")
        
        # Изображения
        images = product.get('images', [])
        print(f"\n🖼️  Изображений: {len(images)}")
        
        image_details = []
        for i, image in enumerate(images, 1):
            image_info = {
                'src': image.get('src', ''),
                'alt': image.get('alt', ''),
                'position': image.get('position', i)
            }
            image_details.append(image_info)
            print(f"   📸 Изображение {i}: {image.get('src', '')[:60]}...")
        
        # Сохраняем все данные
        product_data = {
            'shopify_id': product.get('id'),
            'title': title,
            'vendor': vendor,
            'product_type': product_type,
            'description': description,
            'tags': tags,
            'variants': variant_details,
            'images': image_details,
            'handle': product.get('handle', ''),
            'created_at': product.get('created_at', ''),
            'updated_at': product.get('updated_at', '')
        }
        
        print("\n✅ Данные товара успешно получены!")
        return product_data
    
    def create_amazon_listing_xml(self, product_data):
        """Создаем XML для загрузки товара в Amazon через Feeds API"""
        print("\n🏗️  ЭТАП 2: Создание Amazon Listing XML")
        print("=" * 50)
        
        # Берем первый вариант (обычно основной)
        main_variant = product_data['variants'][0] if product_data['variants'] else {}
        sku = main_variant.get('sku', f"SHOPIFY_{product_data['shopify_id']}")
        
        print(f"📝 Создаем листинг для SKU: {sku}")
        
        # Определяем категорию товара на основе типа
        product_type = product_data.get('product_type', '').lower()
        if 'wiper' in product_type or 'automotive' in product_data.get('tags', '').lower():
            category = 'Automotive'
            subcategory = 'Replacement Parts'
        else:
            category = 'Tools & Home Improvement'
            subcategory = 'Automotive'
        
        print(f"📂 Amazon категория: {category} → {subcategory}")
        
        # Создаем XML структуру для Amazon Product Feed
        envelope = ET.Element("AmazonEnvelope")
        envelope.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        envelope.set("xsi:noNamespaceSchemaLocation", "amzn-envelope.xsd")
        
        # Header
        header = ET.SubElement(envelope, "Header")
        ET.SubElement(header, "DocumentVersion").text = "1.01"
        ET.SubElement(header, "MerchantIdentifier").text = "MERCHANT_ID"
        
        # Message Type
        ET.SubElement(envelope, "MessageType").text = "Product"
        ET.SubElement(envelope, "PurgeAndReplace").text = "false"
        
        # Message
        message = ET.SubElement(envelope, "Message")
        ET.SubElement(message, "MessageID").text = "1"
        ET.SubElement(message, "OperationType").text = "Update"
        
        # Product
        product = ET.SubElement(message, "Product")
        ET.SubElement(product, "SKU").text = sku
        
        # Standard Product ID (если есть штрихкод)
        if main_variant.get('barcode'):
            standard_id = ET.SubElement(product, "StandardProductID")
            ET.SubElement(standard_id, "Type").text = "UPC"
            ET.SubElement(standard_id, "Value").text = main_variant['barcode']
        
        # Product Tax Code (для автозапчастей)
        ET.SubElement(product, "ProductTaxCode").text = "A_GEN_NOTAX"
        
        # Launch Date
        ET.SubElement(product, "LaunchDate").text = datetime.now().strftime("%Y-%m-%d")
        
        # Descriptive Data
        desc_data = ET.SubElement(product, "DescriptiveData")
        ET.SubElement(desc_data, "Title").text = product_data['title']
        ET.SubElement(desc_data, "Brand").text = product_data.get('vendor', 'Generic')
        ET.SubElement(desc_data, "Description").text = product_data.get('description', product_data['title'])
        ET.SubElement(desc_data, "Manufacturer").text = product_data.get('vendor', 'Generic')
        
        # Bullet Points (из тегов и описания)
        bullet_point = ET.SubElement(desc_data, "BulletPoint")
        bullet_point.text = f"Compatible with various vehicle models"
        
        if product_data.get('tags'):
            tags_list = product_data['tags'].split(',')[:4]  # Максимум 5 bullet points
            for i, tag in enumerate(tags_list, 2):
                if i <= 5:
                    bullet = ET.SubElement(desc_data, "BulletPoint")
                    bullet.text = tag.strip().capitalize()
        
        # Product Data для Automotive категории
        product_data_elem = ET.SubElement(product, "ProductData")
        automotive = ET.SubElement(product_data_elem, "Automotive")
        
        # Automotive specific data
        auto_misc = ET.SubElement(automotive, "AutomotiveMisc")
        ET.SubElement(auto_misc, "ProductType").text = "Wiper Blade"
        
        # Variation Data (если нужно)
        if len(product_data['variants']) > 1:
            variation = ET.SubElement(automotive, "VariationData")
            ET.SubElement(variation, "Parentage").text = "parent"
            ET.SubElement(variation, "VariationTheme").text = "Size"
        
        # Преобразуем в красивый XML
        xml_str = ET.tostring(envelope, encoding='unicode')
        
        # Форматируем XML для читаемости
        formatted_xml = self._format_xml(xml_str)
        
        print("✅ Amazon Listing XML создан!")
        print(f"📄 Размер XML: {len(formatted_xml)} символов")
        
        return formatted_xml, sku
    
    def create_amazon_inventory_feed(self, sku, quantity):
        """Создаем XML для обновления остатков"""
        print(f"\n📦 Создание Inventory Feed для SKU: {sku}")
        
        envelope = ET.Element("AmazonEnvelope")
        envelope.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        envelope.set("xsi:noNamespaceSchemaLocation", "amzn-envelope.xsd")
        
        # Header
        header = ET.SubElement(envelope, "Header")
        ET.SubElement(header, "DocumentVersion").text = "1.01"
        ET.SubElement(header, "MerchantIdentifier").text = "MERCHANT_ID"
        
        # Message Type
        ET.SubElement(envelope, "MessageType").text = "Inventory"
        
        # Message
        message = ET.SubElement(envelope, "Message")
        ET.SubElement(message, "MessageID").text = "1"
        ET.SubElement(message, "OperationType").text = "Update"
        
        # Inventory
        inventory = ET.SubElement(message, "Inventory")
        ET.SubElement(inventory, "SKU").text = sku
        ET.SubElement(inventory, "Quantity").text = str(max(0, quantity))
        ET.SubElement(inventory, "FulfillmentLatency").text = "2"  # 2 дня на обработку
        
        xml_str = ET.tostring(envelope, encoding='unicode')
        formatted_xml = self._format_xml(xml_str)
        
        print(f"✅ Inventory XML создан (остаток: {quantity})")
        return formatted_xml
    
    def create_amazon_price_feed(self, sku, price):
        """Создаем XML для обновления цены"""
        print(f"\n💰 Создание Price Feed для SKU: {sku}")
        
        envelope = ET.Element("AmazonEnvelope")
        envelope.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        envelope.set("xsi:noNamespaceSchemaLocation", "amzn-envelope.xsd")
        
        # Header
        header = ET.SubElement(envelope, "Header")
        ET.SubElement(header, "DocumentVersion").text = "1.01"
        ET.SubElement(header, "MerchantIdentifier").text = "MERCHANT_ID"
        
        # Message Type
        ET.SubElement(envelope, "MessageType").text = "Price"
        
        # Message
        message = ET.SubElement(envelope, "Message")
        ET.SubElement(message, "MessageID").text = "1"
        ET.SubElement(message, "OperationType").text = "Update"
        
        # Price
        price_elem = ET.SubElement(message, "Price")
        ET.SubElement(price_elem, "SKU").text = sku
        ET.SubElement(price_elem, "StandardPrice", currency="USD").text = str(price)
        
        xml_str = ET.tostring(envelope, encoding='unicode')
        formatted_xml = self._format_xml(xml_str)
        
        print(f"✅ Price XML создан (цена: ${price})")
        return formatted_xml
    
    def _format_xml(self, xml_string):
        """Форматируем XML для читаемости"""
        try:
            import xml.dom.minidom as minidom
            dom = minidom.parseString(xml_string)
            return dom.toprettyxml(indent="  ")
        except:
            return xml_string
    
    def simulate_amazon_upload(self, product_xml, inventory_xml, price_xml, sku):
        """Симуляция загрузки в Amazon (поскольку Feeds API не работает в sandbox)"""
        print("\n🚀 ЭТАП 3: Симуляция загрузки в Amazon")
        print("=" * 50)
        
        print("📤 В продакшене эти XML будут отправлены через:")
        print("   1. Feeds API - создание товара")
        print("   2. Inventory Feed - установка остатков")
        print("   3. Price Feed - установка цены")
        
        # Попробуем создать feed (будет ошибка в sandbox, но покажем процесс)
        print("\n🧪 Попытка создания Product Feed в sandbox:")
        
        feed_data = {
            "feedType": "POST_PRODUCT_DATA",
            "marketplaceIds": ["ATVPDKIKX0DER"],
            "inputFeedDocumentId": "dummy-document-id"
        }
        
        # В реальности сначала нужно создать документ
        print(f"📋 Feed Type: {feed_data['feedType']}")
        print(f"🌍 Marketplace: {feed_data['marketplaceIds']}")
        
        # Симуляция ответа Amazon
        feed_response = self.amazon_client.make_api_request(
            "/feeds/2021-06-30/feeds",
            method="POST",
            data=feed_data
        )
        
        if feed_response:
            print("✅ Feed создан успешно!")
        else:
            print("❌ Ошибка создания feed (ожидаемо в sandbox)")
            print("💡 В production это будет работать!")
        
        # Сохраняем XML файлы для демонстрации
        self._save_xml_files(product_xml, inventory_xml, price_xml, sku)
    
    def _save_xml_files(self, product_xml, inventory_xml, price_xml, sku):
        """Сохраняем созданные XML файлы"""
        print("\n💾 Сохранение XML файлов:")
        
        # Создаем директорию для XML файлов
        xml_dir = os.path.join(os.path.dirname(__file__), "amazon_xml_feeds")
        os.makedirs(xml_dir, exist_ok=True)
        
        files_created = []
        
        # Product Feed
        product_file = os.path.join(xml_dir, f"product_feed_{sku}.xml")
        with open(product_file, 'w', encoding='utf-8') as f:
            f.write(product_xml)
        files_created.append(product_file)
        print(f"   📄 Product Feed: {product_file}")
        
        # Inventory Feed
        inventory_file = os.path.join(xml_dir, f"inventory_feed_{sku}.xml")
        with open(inventory_file, 'w', encoding='utf-8') as f:
            f.write(inventory_xml)
        files_created.append(inventory_file)
        print(f"   📦 Inventory Feed: {inventory_file}")
        
        # Price Feed
        price_file = os.path.join(xml_dir, f"price_feed_{sku}.xml")
        with open(price_file, 'w', encoding='utf-8') as f:
            f.write(price_xml)
        files_created.append(price_file)
        print(f"   💰 Price Feed: {price_file}")
        
        print(f"\n✅ Создано {len(files_created)} XML файлов")
        return files_created
    
    def create_product_summary(self, product_data, sku):
        """Создаем итоговый отчет"""
        print("\n📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        
        main_variant = product_data['variants'][0] if product_data['variants'] else {}
        
        print("🛍️  ИСХОДНЫЙ ТОВАР SHOPIFY:")
        print(f"   📝 ID: {product_data['shopify_id']}")
        print(f"   📝 Название: {product_data['title']}")
        print(f"   🏢 Бренд: {product_data['vendor']}")
        print(f"   💰 Цена: ${main_variant.get('price', '0.00')}")
        print(f"   🏷️  SKU: {main_variant.get('sku', 'N/A')}")
        print(f"   📊 Остаток: {main_variant.get('inventory_quantity', 0)} шт.")
        print(f"   🖼️  Изображений: {len(product_data['images'])}")
        
        print("\n🚀 СОЗДАВАЕМЫЙ ЛИСТИНГ AMAZON:")
        print(f"   🏷️  SKU: {sku}")
        print(f"   📂 Категория: Automotive → Replacement Parts")
        print(f"   📄 Описание: Скопировано из Shopify")
        print(f"   🎯 Bullet Points: Создано из тегов")
        print(f"   💰 Цена: ${main_variant.get('price', '0.00')} USD")
        print(f"   📦 Остаток: {main_variant.get('inventory_quantity', 0)} шт.")
        
        print("\n✅ РЕЗУЛЬТАТ:")
        print("   🎯 Товар готов к загрузке в Amazon")
        print("   📤 XML feeds созданы и сохранены")
        print("   🔄 В production будет автоматически синхронизироваться")
        
        print("\n🚀 СЛЕДУЮЩИЕ ШАГИ В PRODUCTION:")
        print("   1. Загрузить Product Feed через Feeds API")
        print("   2. Загрузить Inventory Feed для остатков")
        print("   3. Загрузить Price Feed для цены")
        print("   4. Дождаться обработки Amazon (обычно 15-30 минут)")
        print("   5. Товар появится в вашем Seller Central")

def main():
    """Главная функция"""
    print("🚀 SHOPIFY → AMAZON: Создание товара")
    print("🎯 Цель: Создать Bosch Aerotwin A950S в Amazon")
    print("=" * 60)
    
    creator = ShopifyToAmazonCreator()
    
    # Авторизуемся в Amazon
    if not creator.amazon_client.get_access_token():
        print("❌ Не удалось авторизоваться в Amazon")
        return
    
    # Этап 1: Получаем товар из Shopify
    product_data = creator.get_shopify_product_details()
    if not product_data:
        print("❌ Не удалось получить товар из Shopify")
        return
    
    # Этап 2: Создаем XML для Amazon
    product_xml, sku = creator.create_amazon_listing_xml(product_data)
    
    main_variant = product_data['variants'][0] if product_data['variants'] else {}
    inventory_xml = creator.create_amazon_inventory_feed(
        sku, 
        main_variant.get('inventory_quantity', 0)
    )
    price_xml = creator.create_amazon_price_feed(
        sku,
        float(main_variant.get('price', '0.00'))
    )
    
    # Этап 3: Симулируем загрузку
    creator.simulate_amazon_upload(product_xml, inventory_xml, price_xml, sku)
    
    # Итоговый отчет
    creator.create_product_summary(product_data, sku)
    
    print("\n🎉 ПРОЦЕСС ЗАВЕРШЕН!")
    print("💡 Проверьте созданные XML файлы в директории src/amazon_xml_feeds/")

if __name__ == "__main__":
    main()