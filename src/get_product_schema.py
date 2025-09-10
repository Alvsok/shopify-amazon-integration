# -*- coding: utf-8 -*-
"""
Получение полной схемы полей для товара "автомобильные дворники" 
на маркетплейсе Amazon Австралия
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from test_integration import AmazonSandboxClient

# Загружаем переменные окружения
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class AmazonProductSchemaClient:
    """Клиент для получения схем товаров Amazon"""
    
    def __init__(self):
        # Инициализируем базовый клиент для доступа к токенам
        self.base_client = AmazonSandboxClient()
        
        # Маркетплейсы Amazon
        self.marketplaces = {
            'USA': 'ATVPDKIKX0DER',
            'CANADA': 'A2EUQ1WTGCTBG2', 
            'MEXICO': 'A1AM78C64UM0Y8',
            'AUSTRALIA': 'A39IBJ37TRP1C6',  # Австралия
            'UK': 'A1F83G8C2ARO7P',
            'GERMANY': 'A1PA6795UKMFR9',
            'FRANCE': 'A13V1IB3VIYZZH',
            'ITALY': 'APJ6JRA9NG5V4',
            'SPAIN': 'A1RKKUPIHCS9HS',
            'JAPAN': 'A1VC38T7YXB528'
        }
        
        # Возможные типы товаров для автомобильных дворников
        self.wiper_product_types = [
            'WIPER_BLADE',
            'AUTO_PART', 
            'AUTOMOTIVE_REPLACEMENT_PART',
            'WIPER_ARM',
            'WINDSHIELD_WIPER',
            'AUTO_ACCESSORY'
        ]
        
        # Эндпоинты по регионам
        self.endpoints = {
            'NA': 'https://sellingpartnerapi-na.amazon.com',  # США, Канада, Мексика
            'EU': 'https://sellingpartnerapi-eu.amazon.com',  # Европа
            'FE': 'https://sellingpartnerapi-fe.amazon.com'   # Дальний Восток (включая Австралию)
        }
    
    def get_region_endpoint(self, marketplace_id):
        """Определяет нужный эндпоинт по ID маркетплейса"""
        if marketplace_id in ['ATVPDKIKX0DER', 'A2EUQ1WTGCTBG2', 'A1AM78C64UM0Y8']:
            return self.endpoints['NA']
        elif marketplace_id in ['A39IBJ37TRP1C6', 'A1VC38T7YXB528']:  # Австралия, Япония
            return self.endpoints['FE']
        else:
            return self.endpoints['EU']  # Европа по умолчанию
    
    def search_product_types(self, marketplace_id, keywords='wiper'):
        """Ищет доступные типы товаров по ключевым словам"""
        print(f"🔍 Поиск типов товаров по ключевому слову: {keywords}")
        print(f"📍 Маркетплейс: {marketplace_id}")
        
        try:
            # Получаем токен доступа
            access_token = self.base_client.get_access_token()
            if not access_token:
                print("❌ Не удалось получить токен доступа")
                return None
            
            # Определяем эндпоинт
            base_url = self.get_region_endpoint(marketplace_id)
            
            headers = {
                'x-amz-access-token': access_token,
                'Content-Type': 'application/json'
            }
            
            api_version = "2020-09-01"
            url = f"{base_url}/definitions/{api_version}/productTypes"
            
            params = {
                'marketplaceIds': marketplace_id
            }
            
            print(f"🌐 Запрос к: {url}")
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            product_types = data.get('productTypes', [])
            
            print(f"✅ Найдено {len(product_types)} типов товаров")
            
            # Фильтруем по ключевым словам
            matching_types = []
            for ptype in product_types:
                name = ptype.get('name', '').upper()
                display_name = ptype.get('displayName', '').upper()
                
                if any(keyword.upper() in name or keyword.upper() in display_name 
                      for keyword in keywords.split()):
                    matching_types.append(ptype)
            
            print(f"🎯 Найдено {len(matching_types)} подходящих типов:")
            for ptype in matching_types:
                print(f"   • {ptype.get('name')} - {ptype.get('displayName')}")
            
            # Сохраняем полный список
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"product_types_{marketplace_id}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'marketplace_id': marketplace_id,
                    'total_types': len(product_types),
                    'matching_types': matching_types,
                    'all_types': product_types
                }, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Результаты сохранены в: {filename}")
            return matching_types
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при поиске типов товаров: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Код ответа: {e.response.status_code}")
                print(f"   Тело ответа: {e.response.text}")
            return None
    
    def get_product_type_definition(self, product_type, marketplace_id):
        """Получает полную схему определения типа товара"""
        print(f"⚙️  Запрашиваем схему для типа '{product_type}'...")
        print(f"📍 Маркетплейс: {marketplace_id}")
        
        try:
            # Получаем токен доступа
            access_token = self.base_client.get_access_token()
            if not access_token:
                print("❌ Не удалось получить токен доступа")
                return None
            
            # Определяем эндпоинт
            base_url = self.get_region_endpoint(marketplace_id)
            
            headers = {
                'x-amz-access-token': access_token,
                'Content-Type': 'application/json'
            }
            
            api_version = "2020-09-01"
            url = f"{base_url}/definitions/{api_version}/productTypes/{product_type}"
            
            params = {
                'marketplaceIds': marketplace_id,
                'requirements': 'LISTING',  # Требования для создания листинга
                'requirementsEnforced': 'ENFORCED'  # Только обязательные поля
            }
            
            print(f"🌐 Запрос к: {url}")
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            schema = response.json()
            print("✅ Схема успешно получена!")
            
            # Анализируем схему
            self.analyze_schema(schema, product_type)
            
            # Сохраняем результат
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"schema_{product_type}_{marketplace_id}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Схема сохранена в: {filename}")
            return schema
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при запросе схемы: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Код ответа: {e.response.status_code}")
                print(f"   Тело ответа: {e.response.text}")
            return None
    
    def analyze_schema(self, schema, product_type):
        """Анализирует и выводит информацию о схеме"""
        print("\n" + "="*60)
        print(f"📊 АНАЛИЗ СХЕМЫ ДЛЯ ТИПА: {product_type}")
        print("="*60)
        
        # Основная информация
        schema_info = schema.get('schema', {})
        properties = schema_info.get('properties', {})
        required = schema_info.get('required', [])
        
        print(f"📋 Всего полей в схеме: {len(properties)}")
        print(f"🔴 Обязательных полей: {len(required)}")
        
        if required:
            print("\n🔴 ОБЯЗАТЕЛЬНЫЕ ПОЛЯ:")
            print("-" * 40)
            for field in required:
                field_info = properties.get(field, {})
                field_type = field_info.get('type', 'unknown')
                description = field_info.get('description', 'Нет описания')
                
                print(f"• {field}")
                print(f"  Тип: {field_type}")
                print(f"  Описание: {description[:100]}{'...' if len(description) > 100 else ''}")
                
                # Дополнительные ограничения
                if 'enum' in field_info:
                    print(f"  Допустимые значения: {field_info['enum'][:5]}{'...' if len(field_info['enum']) > 5 else ''}")
                if 'maxLength' in field_info:
                    print(f"  Макс. длина: {field_info['maxLength']}")
                if 'pattern' in field_info:
                    print(f"  Формат: {field_info['pattern']}")
                print()
        
        # Опциональные поля (первые 10)
        optional_fields = [f for f in properties.keys() if f not in required]
        if optional_fields:
            print(f"\n💙 ОПЦИОНАЛЬНЫЕ ПОЛЯ (показано первые 10 из {len(optional_fields)}):")
            print("-" * 50)
            for field in optional_fields[:10]:
                field_info = properties.get(field, {})
                field_type = field_info.get('type', 'unknown')
                description = field_info.get('description', 'Нет описания')
                
                print(f"• {field} ({field_type})")
                print(f"  {description[:80]}{'...' if len(description) > 80 else ''}")
        
        print("\n" + "="*60)
    
    def test_all_wiper_types(self, marketplace_id):
        """Тестирует все возможные типы товаров для дворников"""
        print("🧪 ТЕСТИРУЕМ ВСЕ ВОЗМОЖНЫЕ ТИПЫ ДВОРНИКОВ")
        print("="*50)
        
        successful_types = []
        
        for product_type in self.wiper_product_types:
            print(f"\n🔍 Тестируем тип: {product_type}")
            schema = self.get_product_type_definition(product_type, marketplace_id)
            
            if schema:
                successful_types.append(product_type)
                print(f"✅ {product_type} - схема получена")
            else:
                print(f"❌ {product_type} - не найден или ошибка")
        
        print(f"\n📊 ИТОГО:")
        print(f"✅ Успешно получены схемы для: {successful_types}")
        print(f"❌ Не найдены: {[t for t in self.wiper_product_types if t not in successful_types]}")
        
        return successful_types

def main():
    """Основная функция"""
    print("🚀 ПОЛУЧЕНИЕ СХЕМЫ ТОВАРА 'АВТОМОБИЛЬНЫЕ ДВОРНИКИ'")
    print("🇦🇺 МАРКЕТПЛЕЙС: Amazon Австралия")
    print("="*60)
    
    client = AmazonProductSchemaClient()
    australia_marketplace = client.marketplaces['AUSTRALIA']
    
    # 1. Сначала ищем доступные типы товаров
    print("📋 ШАГ 1: Поиск подходящих типов товаров")
    matching_types = client.search_product_types(australia_marketplace, 'wiper blade auto part')
    
    if matching_types:
        print(f"\n🎯 Найдены подходящие типы:")
        for ptype in matching_types:
            print(f"   • {ptype.get('name')} - {ptype.get('displayName')}")
        
        # 2. Получаем схему для первого найденного типа
        first_type = matching_types[0]['name']
        print(f"\n📋 ШАГ 2: Получение схемы для типа '{first_type}'")
        schema = client.get_product_type_definition(first_type, australia_marketplace)
        
    else:
        print("\n⚠️  Подходящие типы не найдены через поиск.")
        print("📋 ШАГ 2: Тестируем предопределенные типы")
        
        # 3. Тестируем все возможные типы
        successful_types = client.test_all_wiper_types(australia_marketplace)
        
        if successful_types:
            print(f"\n✅ Рекомендуемый тип товара: {successful_types[0]}")
        else:
            print("\n❌ Не удалось найти подходящий тип товара")
            print("💡 Возможные причины:")
            print("   • Ограничения Sandbox окружения")
            print("   • Нужны дополнительные права доступа")
            print("   • Неправильные названия типов товаров")

if __name__ == '__main__':
    main()