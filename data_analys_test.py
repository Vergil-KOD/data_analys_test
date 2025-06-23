import re
import requests
import json
from time import sleep

def is_valid_ip(ip):
    """Проверяет, является ли строка корректным IPv4 или IPv6 адресом."""
    ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    if re.match(ipv4_pattern, ip):
        return "IPv4"
    elif re.match(ipv6_pattern, ip):
        return "IPv6"
    return None

def get_ip_geolocation(ip):
    """Получает геолокацию IP-адреса с помощью API ip-api.com."""
    url = f"http://ip-api.com/json/{ip}"
    try:
        response = requests.get(url, timeout=10)
        
        # Проверка на лимит запросов (HTTP 429)
        if response.status_code == 429:
            return {"error": "API error: Слишком много запросов. Попробуйте позже."}
            
        # Проверка на другие ошибки API
        if response.status_code != 200:
            return {"error": f"API error: HTTP {response.status_code}"}
            
        data = response.json()
        
        # Проверка на ошибку в ответе API
        if data.get('status') == 'fail':
            return {"error": f"API error: {data.get('message', 'Unknown error')}"}
            
        return data
        
    except requests.exceptions.Timeout:
        return {"error": "Проблема с сетью: Таймаут запроса. Проверьте подключение к интернету."}
    except requests.exceptions.ConnectionError:
        return {"error": "Проблема с сетью: Не удалось подключиться к API. Проверьте подключение к интернету."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Проблема с сетью: {str(e)}"}

def print_geolocation(data):
    """Выводит информацию о геолокации в удобном формате."""
    if "error" in data:
        print(f"\nОшибка: {data['error']}\n")
        return False
    else:
        print("\n--- Геолокация IP ---")
        print(f"IP: {data.get('query', 'N/A')}")
        print(f"Страна: {data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})")
        print(f"Регион: {data.get('regionName', 'N/A')} ({data.get('region', 'N/A')})")
        print(f"Город: {data.get('city', 'N/A')}")
        print(f"Координаты: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
        print(f"Провайдер: {data.get('isp', 'N/A')}")
        print(f"Организация: {data.get('org', 'N/A')}")
        print("----------------------\n")
        return True

def get_external_ip():
    """Получает внешний IP пользователя с резервными серверами."""
    services = [
        "https://api.ipify.org?format=json",
        "https://ipinfo.io/json",
        "https://ifconfig.me/all.json"
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=3)
            if response.status_code == 200:
                return response.json().get("ip")
        except:
            continue
    return None

def main():
    print("IP-адрес и геолокация (введите 'exit' для выхода)\n")
    
    while True:
        user_input = input("Введите IP-адрес (или оставьте пустым для вашего IP): ").strip()
        
        if user_input.lower() == 'exit':
            print("Выход из программы.")
            break
        
        if not user_input:
            print("\nОпределение вашего внешнего IP...")
            user_ip = get_external_ip()
            
            if user_ip:
                print(f"Ваш внешний IP: {user_ip}")
                user_input = user_ip
            else:
                print("Ошибка: Не удалось определить ваш IP. Пожалуйста, введите его вручную.\n")
                continue
        
        ip_type = is_valid_ip(user_input)
        
        if ip_type:
            print(f"\nПроверка {ip_type} адреса: {user_input}...")
            
            # Добавляем задержку для соблюдения лимита API
            sleep(1.5)
            
            geodata = get_ip_geolocation(user_input)
            print_geolocation(geodata)
        else:
            print("Ошибка: Некорректный IP-адрес. Попробуйте снова.\n")

if __name__ == "__main__":
    main()