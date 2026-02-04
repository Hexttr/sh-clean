#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для настройки .env файла на сервере с API ключом
"""
import os
import sys
import paramiko
from dotenv import load_dotenv

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

def setup_env_file():
    """Настройка .env файла на сервере"""
    host = os.getenv('SSH_HOST')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
    port = int(os.getenv('SSH_PORT', 22))
    
    # Получаем API ключ из локального .env или из аргументов командной строки
    api_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        try:
            api_key = input("Введите ANTHROPIC_API_KEY (или нажмите Enter для пропуска): ").strip()
        except EOFError:
            print("[INFO] Интерактивный ввод недоступен. Используйте:")
            print("  python setup_env_on_server.py <your-api-key>")
            print("  или добавьте ANTHROPIC_API_KEY в локальный .env файл")
            api_key = ''
    
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
        
        print("[OK] Подключено!")
        
        if api_key:
            # Обновляем .env файл
            env_content = f"""# Anthropic API Key (required)
ANTHROPIC_API_KEY={api_key}

# Optional: Claude Code OAuth Token
# CLAUDE_CODE_OAUTH_TOKEN=

# Recommended: Max output tokens
CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000

# Optional: Router Mode (Alternative Providers)
# OPENAI_API_KEY=
# OPENROUTER_API_KEY=
# ROUTER_DEFAULT=openai,gpt-4o
"""
            sftp = client.open_sftp()
            remote_file = sftp.file('/root/shannon/.env', 'w')
            remote_file.write(env_content)
            remote_file.close()
            sftp.close()
            print("[OK] .env файл обновлен с API ключом")
        else:
            print("[INFO] API ключ не указан, файл .env не изменен")
            print("Вы можете отредактировать /root/shannon/.env вручную")
        
        # Проверяем docker-compose
        print("\n=== Проверка Docker Compose ===")
        stdin, stdout, stderr = client.exec_command('which docker-compose || docker compose version')
        compose_check = stdout.read().decode().strip()
        if compose_check:
            print(f"Docker Compose: {compose_check}")
        else:
            print("[WARNING] Docker Compose не найден. Устанавливаем...")
            execute_command(client, 
                "curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose",
                "Установка Docker Compose")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        return False

def execute_command(client, command, description):
    """Выполняет команду на сервере"""
    print(f"--- {description} ---")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    if output:
        print(output)

if __name__ == "__main__":
    setup_env_file()

