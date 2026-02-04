#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для подготовки сервера: удаление старого приложения и настройка окружения
"""
import os
import sys
import paramiko
from dotenv import load_dotenv

# Исправляем кодировку для Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

def execute_command(client, command, description):
    """Выполняет команду на сервере и выводит результат"""
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

def prepare_server():
    """Подготовка сервера для нового приложения"""
    host = os.getenv('SSH_HOST')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
    port = int(os.getenv('SSH_PORT', 22))
    
    print(f"Подключение к серверу {host}...")
    
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
        
        print("[OK] Успешное подключение к серверу!")
        
        # Останавливаем старые процессы
        print("\n=== Остановка старых процессов ===")
        execute_command(client, "pkill -f 'web-interface.cjs'", "Остановка web-interface")
        execute_command(client, "pkill -f 'cometapi_proxy.js'", "Остановка cometapi_proxy")
        
        # Останавливаем старые контейнеры (кроме juice-shop, если нужен)
        print("\n=== Остановка старых контейнеров ===")
        execute_command(client, "docker ps -a --format '{{.Names}}' | grep -v juice-shop | xargs -r docker stop", 
                      "Остановка контейнеров (кроме juice-shop)")
        execute_command(client, "docker ps -a --format '{{.Names}}' | grep -v juice-shop | xargs -r docker rm", 
                      "Удаление остановленных контейнеров")
        
        # Удаляем старое приложение
        print("\n=== Удаление старого приложения ===")
        execute_command(client, "rm -rf /root/shannon-uncontained", "Удаление shannon-uncontained")
        
        # Проверяем наличие необходимых инструментов
        print("\n=== Проверка окружения ===")
        execute_command(client, "docker --version", "Версия Docker")
        execute_command(client, "node --version", "Версия Node.js")
        execute_command(client, "npm --version", "Версия npm")
        execute_command(client, "which git", "Проверка Git")
        
        # Создаем директорию для нового приложения
        print("\n=== Подготовка директории для нового приложения ===")
        execute_command(client, "mkdir -p /root/sh-clean", "Создание директории sh-clean")
        execute_command(client, "cd /root/sh-clean && pwd", "Проверка директории")
        
        # Проверяем доступное место на диске
        print("\n=== Проверка дискового пространства ===")
        execute_command(client, "df -h /", "Использование диска")
        
        # Проверяем порты
        print("\n=== Проверка используемых портов ===")
        execute_command(client, "netstat -tuln | grep -E ':(7233|8233|3000|3001|3456)' || ss -tuln | grep -E ':(7233|8233|3000|3001|3456)'", 
                      "Проверка портов (7233, 8233, 3000, 3001, 3456)")
        
        print("\n[OK] Сервер подготовлен для нового приложения!")
        print("\nСледующие шаги:")
        print("1. Загрузить код приложения на сервер")
        print("2. Установить зависимости (npm install)")
        print("3. Настроить .env файл")
        print("4. Запустить приложение")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        return False

if __name__ == "__main__":
    import sys
    print("=" * 60)
    print("Подготовка сервера для sh-clean")
    print("=" * 60)
    
    # Если передан аргумент --yes, пропускаем подтверждение
    if len(sys.argv) > 1 and sys.argv[1] in ['--yes', '-y']:
        prepare_server()
    else:
        try:
            response = input("\nВы уверены, что хотите удалить старое приложение? (yes/no): ")
            if response.lower() in ['yes', 'y', 'да', 'д']:
                prepare_server()
            else:
                print("Операция отменена.")
        except EOFError:
            # Автоматический режим при отсутствии интерактивного ввода
            print("\nАвтоматический режим: пропускаем подтверждение")
            prepare_server()

