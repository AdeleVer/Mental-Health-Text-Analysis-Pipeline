import requests
import json

# 1. Логин для получения токена
login_url = "http://localhost:5000/api/auth/login"
login_data = {
    "username": "Adele",
    "password": "331123Aver."
}

response = requests.post(login_url, json=login_data)
token = response.json()["token"]
print("Токен получен!")

# 2. Анализ текста с токеном
analyze_url = "http://localhost:5000/api/analyze"
analyze_data = {
    "text": "Я чувствую тревогу и беспокойство сегодня, но стараюсь сохранять спокойствие",
    "language": "ru"
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

response = requests.post(analyze_url, json=analyze_data, headers=headers)
print("Результат анализа:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))