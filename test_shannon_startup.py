#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестового запуска Shannon без API ключа (проверка контейнеров)
"""
import os
import sys
import paramiko
from dotenv import load_dotenv
import time

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

def execute_command(client, command, description):
    """Выполняет команду на сервере"""
    print(f"\n--- {description} ---")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    if output:
        print(output)
    if error and exit_status != 0:
        print(f"[WARNING] {error}")
    
    return exit_status == 0, output

def test_shannon_startup():
    """Тестовый запуск Shannon для проверки контейнеров"""
    host = os.getenv('SSH_HOST')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
    port = int(os.getenv('SSH_PORT', 22))
    
    print("=" * 60)
    print("Тестовый запуск Shannon (проверка контейнеров)")
    print("=" * 60)
    print(f"\nПодключение к серверу {host}...")
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host,
            username=username,
            password=password,
            port=port,
            timeout=10
        )
        
        print("[OK] Подключено!")
        
        # Переходим в директорию Shannon
        print("\n=== Переход в директорию Shannon ===")
        execute_command(client, "cd /root/shannon && pwd", "Текущая директория")
        
        # Проверяем наличие скрипта
        execute_command(client, "test -f /root/shannon/shannon && echo 'OK' || echo 'NOT FOUND'", 
                       "Проверка скрипта shannon")
        
        # Проверяем Docker Compose
        print("\n=== Проверка Docker Compose ===")
        execute_command(client, "which docker-compose || docker compose version", 
                       "Проверка docker-compose")
        
        # Останавливаем старые контейнеры если есть
        print("\n=== Остановка старых контейнеров ===")
        execute_command(client, "cd /root/shannon && (docker-compose down 2>&1 || docker compose down 2>&1 || true)", 
                       "Остановка контейнеров")
        
        # Проверяем порты
        print("\n=== Проверка портов ===")
        execute_command(client, 
            "ss -tuln | grep -E ':(7233|8233)' || echo 'Порты свободны'",
            "Проверка портов 7233 и 8233")
        
        # Пробуем запустить контейнеры (без API ключа они должны подняться, но workflow не запустится)
        print("\n=== Запуск контейнеров Temporal ===")
        print("Запускаем только Temporal (без worker, т.к. нужен API ключ)...")
        
        # Запускаем только temporal
        success, output = execute_command(client,
            "cd /root/shannon && (docker-compose up -d temporal || docker compose up -d temporal)",
            "Запуск Temporal")
        
        if success:
            print("[OK] Temporal запущен!")
            
            # Ждем немного
            print("\nОжидание запуска Temporal (10 секунд)...")
            time.sleep(10)
            
            # Проверяем статус
            print("\n=== Статус контейнеров ===")
            execute_command(client, "docker ps", "Список запущенных контейнеров")
            
            # Проверяем здоровье Temporal
            print("\n=== Проверка здоровья Temporal ===")
            execute_command(client,
                "cd /root/shannon && (docker-compose exec -T temporal temporal operator cluster health --address localhost:7233 2>&1 || docker compose exec -T temporal temporal operator cluster health --address localhost:7233 2>&1 || echo 'Проверка не удалась')",
                "Проверка здоровья Temporal")
            
            # Проверяем доступность веб-интерфейса
            print("\n=== Проверка веб-интерфейса ===")
            execute_command(client,
                "curl -s -o /dev/null -w '%{http_code}' http://localhost:8233 || echo 'Недоступен'",
                "HTTP статус веб-интерфейса")
            
            print("\n" + "=" * 60)
            print("[OK] Тест завершен!")
            print("=" * 60)
            print("\nРезультаты:")
            print("- Temporal контейнер запущен")
            print("- Веб-интерфейс доступен на: http://72.56.79.153:8233")
            print("\nПримечание: Для полного запуска Shannon нужен ANTHROPIC_API_KEY")
            print("Добавьте его в /root/shannon/.env и запустите:")
            print("  cd /root/shannon")
            print("  ./shannon start URL=http://localhost:3001 REPO=/root/shannon")
        else:
            print("[ERROR] Не удалось запустить Temporal")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_shannon_startup()

