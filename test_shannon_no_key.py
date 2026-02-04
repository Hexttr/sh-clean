#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый запуск Shannon без API ключа - проверка что контейнеры поднимаются
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

def execute_command(client, command, description, wait_for_output=True):
    """Выполняет команду на сервере"""
    print(f"\n--- {description} ---")
    stdin, stdout, stderr = client.exec_command(command)
    
    if wait_for_output:
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        if output:
            print(output)
        if error and exit_status != 0:
            print(f"[WARNING] {error}")
        
        return exit_status == 0, output
    else:
        # Для длительных команд
        return True, ""

def test_shannon_no_key():
    """Тестовый запуск Shannon без API ключа"""
    host = os.getenv('SSH_HOST')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
    port = int(os.getenv('SSH_PORT', 22))
    
    print("=" * 60)
    print("Тестовый запуск Shannon БЕЗ API ключа")
    print("=" * 60)
    print("\nОжидаемое поведение:")
    print("- Контейнеры должны подняться")
    print("- Но workflow не запустится без API ключа")
    print("=" * 60)
    
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
        
        print("\n[OK] Подключено к серверу")
        
        # Останавливаем старые контейнеры
        print("\n=== Остановка старых контейнеров ===")
        execute_command(client, "cd /root/shannon && docker-compose down 2>&1 || true", 
                       "Остановка контейнеров")
        
        # Пробуем запустить Shannon без ключа
        print("\n=== Попытка запуска Shannon ===")
        print("Команда: ./shannon start URL=http://localhost:3001 REPO=/root/shannon")
        print("\nОжидаем ошибку об отсутствии API ключа...")
        
        stdin, stdout, stderr = client.exec_command(
            "cd /root/shannon && ./shannon start URL=http://localhost:3001 REPO=/root/shannon 2>&1"
        )
        
        # Ждем завершения
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print("\nВывод команды:")
        print(output)
        if error:
            print("\nОшибки:")
            print(error)
        
        # Проверяем статус контейнеров
        print("\n=== Статус контейнеров ===")
        execute_command(client, "docker ps -a", "Список контейнеров")
        
        # Проверяем логи если контейнеры запущены
        stdin, stdout, stderr = client.exec_command("docker ps --format '{{.Names}}' | grep -E '(temporal|worker)'")
        containers = stdout.read().decode('utf-8').strip()
        
        if containers:
            print(f"\nНайдены контейнеры: {containers}")
            print("\n=== Логи Temporal ===")
            execute_command(client, "docker-compose -f /root/shannon/docker-compose.yml logs --tail=20 temporal 2>&1 || true",
                           "Последние логи Temporal")
        
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ ТЕСТА:")
        print("=" * 60)
        
        if "ERROR" in output.upper() or "ANTHROPIC_API_KEY" in output.upper():
            print("[OK] Shannon корректно требует API ключ")
        else:
            print("[INFO] Не удалось определить требование API ключа из вывода")
        
        if containers:
            print("[OK] Контейнеры запущены (Temporal работает)")
            print("[INFO] Для полного запуска добавьте ANTHROPIC_API_KEY в .env")
        else:
            print("[INFO] Контейнеры не запущены (возможно, из-за отсутствия API ключа)")
        
        print("\nВеб-интерфейс Temporal: http://72.56.79.153:8233")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_shannon_no_key()

