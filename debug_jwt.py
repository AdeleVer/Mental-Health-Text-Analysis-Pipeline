import os
import jwt
from datetime import datetime, timezone
from src.auth.utils import generate_jwt_token, verify_jwt_token

# Проверяем переменные окружения
print("=== ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===")
print(f"JWT_SECRET: {os.getenv('JWT_SECRET')}")
print(f"ENCRYPTION_KEY: {os.getenv('ENCRYPTION_KEY')}")

# Тестируем JWT отдельно
print("\n=== ТЕСТ JWT ===")
test_user_id = 1

# Генерируем токен
token = generate_jwt_token(test_user_id)
print(f"Сгенерированный токен: {token}")

# Пробуем декодировать
decoded_id = verify_jwt_token(token)
print(f"Декодированный ID: {decoded_id}")
print(f"Совпадает? {decoded_id == test_user_id}")

# Проверяем вручную
print("\n=== РУЧНАЯ ПРОВЕРКА ===")
try:
    secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    print(f"Ручное декодирование: {payload}")
except Exception as e:
    print(f"Ошибка ручного декодирования: {e}")