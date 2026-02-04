#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для развертывания оригинального Shannon на сервере
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

def execute_command(client, command, description, check_output=False):
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
    
    if check_output and exit_status != 0:
        return False, output
    return exit_status == 0, output

def deploy_shannon():
    """Развертывание оригинального Shannon на сервере"""
    host = os.getenv('SSH_HOST')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
    port = int(os.getenv('SSH_PORT', 22))
    
    print("=" * 60)
    print("Развертывание оригинального Shannon на сервере")
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
        
        print("[OK] Успешное подключение к серверу!")
        
        # Проверяем, существует ли уже директория shannon
        print("\n=== Проверка существующей установки ===")
        stdin, stdout, stderr = client.exec_command('test -d /root/shannon && echo "exists" || echo "not_exists"')
        shannon_exists = stdout.read().decode().strip()
        
        if shannon_exists == "exists":
            print("Директория /root/shannon уже существует")
            response = input("Удалить и переустановить? (yes/no): ").lower()
            if response in ['yes', 'y', 'да', 'д']:
                execute_command(client, "rm -rf /root/shannon", "Удаление старой установки")
            else:
                print("Продолжаем с существующей установкой...")
        
        # Клонируем репозиторий Shannon
        print("\n=== Клонирование репозитория Shannon ===")
        if shannon_exists == "exists" and response not in ['yes', 'y', 'да', 'д']:
            print("Пропускаем клонирование (используем существующую установку)")
        else:
            execute_command(client, 
                "cd /root && git clone https://github.com/KeygraphHQ/shannon.git",
                "Клонирование репозитория")
        
        # Переходим в директорию shannon
        print("\n=== Настройка проекта ===")
        execute_command(client, "cd /root/shannon && pwd", "Текущая директория")
        
        # Проверяем наличие .env файла
        stdin, stdout, stderr = client.exec_command('test -f /root/shannon/.env && echo "exists" || echo "not_exists"')
        env_exists = stdout.read().decode().strip()
        
        if env_exists == "not_exists":
            print("\n=== Создание .env файла ===")
            # Создаем базовый .env файл
            env_content = """# Anthropic API Key (required)
ANTHROPIC_API_KEY=

# Optional: Claude Code OAuth Token
# CLAUDE_CODE_OAUTH_TOKEN=

# Recommended: Max output tokens
CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000

# Optional: Router Mode (Alternative Providers)
# OPENAI_API_KEY=
# OPENROUTER_API_KEY=
# ROUTER_DEFAULT=openai,gpt-4o
"""
            # Записываем .env файл на сервер
            sftp = client.open_sftp()
            remote_file = sftp.file('/root/shannon/.env', 'w')
            remote_file.write(env_content)
            remote_file.close()
            sftp.close()
            print("[OK] Файл .env создан")
            print("\n[ВАЖНО] Не забудьте добавить ANTHROPIC_API_KEY в /root/shannon/.env")
        else:
            print("[OK] Файл .env уже существует")
        
        # Делаем скрипт shannon исполняемым
        print("\n=== Настройка прав доступа ===")
        execute_command(client, "chmod +x /root/shannon/shannon", "Установка прав на скрипт shannon")
        
        # Проверяем Docker
        print("\n=== Проверка Docker ===")
        execute_command(client, "docker --version", "Версия Docker")
        execute_command(client, "docker compose version", "Версия Docker Compose")
        
        # Проверяем порты
        print("\n=== Проверка портов ===")
        execute_command(client, 
            "ss -tuln | grep -E ':(7233|8233)' || echo 'Порты 7233 и 8233 свободны'",
            "Проверка портов Temporal (7233 - gRPC, 8233 - Web UI)")
        
        print("\n" + "=" * 60)
        print("[OK] Развертывание завершено!")
        print("=" * 60)
        
        print("\nСледующие шаги:")
        print("1. Добавьте ANTHROPIC_API_KEY в /root/shannon/.env на сервере")
        print("2. Запустите Shannon:")
        print("   ssh root@72.56.79.153")
        print("   cd /root/shannon")
        print("   ./shannon start URL=https://your-app.com REPO=/path/to/repo")
        print("\n3. Мониторинг:")
        print("   ./shannon logs ID=<workflow-id>")
        print("   ./shannon query ID=<workflow-id>")
        print("   http://72.56.79.153:8233 - Temporal Web UI")
        print("\n4. Остановка:")
        print("   ./shannon stop")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    deploy_shannon()

