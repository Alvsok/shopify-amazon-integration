# Shopify-Amazon Integration Setup

## Что сделано

✅ Весь код перенесен в файл `src/test_integration.py`
✅ Настроено использование файла `.env` для всех чувствительных данных
✅ Проверен и обновлен `requirements.txt` со всеми необходимыми зависимостями
✅ Создан полнофункциональный тестовый скрипт для Amazon Sandbox и Shopify API

## Структура проекта

```
shopify-amazon-integration/
├── .env                    # Конфигурация с чувствительными данными
├── requirements.txt        # Python зависимости
├── src/
│   └── test_integration.py # Основной интеграционный тестовый скрипт
└── venv/                  # Виртуальное окружение
```

## Установка и настройка

### 1. Получите Amazon Sandbox credentials

1. Перейдите в [Amazon SP-API Console](https://developer-docs.amazon.com/sp-api/page/sp-api-sandbox)
2. Найдите вашу aplikацию и нажмите "View sandbox credentials"
3. Скопируйте:
   - Client ID
   - Client Secret  
   - Refresh Token для sandbox

### 2. Настройте .env файл

Откройте файл `.env` и замените placeholder-ы на реальные данные:

```bash
# Amazon Selling Partner API Credentials (Sandbox)
AMAZON_CLIENT_ID=amzn1.sp.solution.4be3f013-45c7-4d0f-87da-95c8de7d9ed0
AMAZON_CLIENT_SECRET=ваш_реальный_client_secret
AMAZON_REFRESH_TOKEN=ваш_реальный_refresh_token

# Shopify API Credentials (Опционально)
SHOPIFY_SHOP_DOMAIN=ваш-магазин
SHOPIFY_ACCESS_TOKEN=ваш_shopify_токен
SHOPIFY_API_VERSION=2023-10
```

### 3. Установите зависимости

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

## Запуск тестов

### Полный интеграционный тест
```bash
python src/test_integration.py
```

### Только Amazon Sandbox тест
```python
from src.test_integration import test_amazon_sandbox
test_amazon_sandbox()
```

## Что включает в себя test_integration.py

### Классы:
- **AmazonSandboxClient**: Клиент для работы с Amazon SP-API Sandbox
- **ShopifyClient**: Клиент для работы с Shopify API
- **IntegrationTester**: Основной класс для запуска всех тестов

### Функциональность:
- ✅ Автоматическое получение access token для Amazon API
- ✅ Тестирование Amazon Listings API
- ✅ Тестирование Amazon Orders API
- ✅ Тестирование Shopify Products API
- ✅ Тестирование Shopify Orders API
- ✅ Проверка переменных окружения
- ✅ Детальное логирование всех операций
- ✅ Обработка ошибок и исключений

## Пример вывода

```
🚀 Starting Full Integration Test Suite
==================================================
Testing environment variables...
✅ All environment variables are set

🔄 Testing Amazon Sandbox API...
✅ Successfully obtained Amazon access token
Testing Amazon Listings API endpoint...
✅ Listings endpoint test successful
Testing Amazon Orders API endpoint...
✅ Orders endpoint test successful
✅ All Amazon sandbox tests passed

🔄 Testing Shopify API...
Testing Shopify Products API endpoint...
✅ Products endpoint test successful
Found 12 products
Testing Shopify Orders API endpoint...
✅ Orders endpoint test successful
Found 5 orders
✅ All Shopify API tests passed

==================================================
🎉 All integration tests passed successfully!
```

## Requirements.txt

Все необходимые зависимости уже включены:
- `requests==2.32.5` - для HTTP запросов
- `python-dotenv==1.1.1` - для загрузки .env файла
- `certifi==2025.8.3` - для SSL сертификатов
- `charset-normalizer==3.4.3` - для кодировки
- `idna==3.10` - для internationalized domain names
- `urllib3==2.5.0` - для HTTP клиента

## Следующие шаги

1. Замените placeholder-ы в `.env` на реальные sandbox credentials
2. Запустите `python src/test_integration.py` для тестирования
3. После успешного тестирования sandbox, настройте production credentials
4. Расширьте функциональность по необходимости