#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый запуск Shannon с API ключом
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

def test_shannon_with_key():
    """Тестовый запуск Shannon с API ключом"""
    host = os.getenv('SSH_HOST')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
    port = int(os.getenv('SSH_PORT', 22))
    
    print("=" * 60)
    print("Тестовый запуск Shannon С API ключом")
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
        
        # Проверяем наличие ключа в .env
        print("\n=== Проверка .env файла ===")
        stdin, stdout, stderr = client.exec_command("grep -c 'ANTHROPIC_API_KEY' /root/shannon/.env || echo '0'")
        key_count = stdout.read().decode('utf-8').strip()
        if key_count != '0':
            print("[OK] API ключ найден в .env")
        else:
            print("[ERROR] API ключ не найден!")
            return False
        
        # Проверяем что ключ не пустой
        stdin, stdout, stderr = client.exec_command("grep 'ANTHROPIC_API_KEY=' /root/shannon/.env | cut -d'=' -f2 | wc -c")
        key_length = int(stdout.read().decode('utf-8').strip())
        if key_length > 10:
            print(f"[OK] Длина ключа: {key_length} символов")
        else:
            print("[ERROR] Ключ слишком короткий или пустой!")
            return False
        
        # Пробуем запустить Shannon
        print("\n=== Запуск Shannon ===")
        print("Команда: ./shannon start URL=http://localhost:3001 REPO=/root/shannon")
        print("\nЗапускаем в фоне...")
        
        # Запускаем команду в фоне
        stdin, stdout, stderr = client.exec_command(
            "cd /root/shannon && nohup ./shannon start URL=http://localhost:3001 REPO=/root/shannon > /tmp/shannon_start.log 2>&1 &"
        )
        time.sleep(3)
        
        # Проверяем логи запуска
        print("\n=== Логи запуска ===")
        execute_command(client, "tail -30 /tmp/shannon_start.log 2>&1 || echo 'Логи еще не созданы'",
                       "Последние логи")
        
        # Проверяем статус контейнеров
        print("\n=== Статус контейнеров ===")
        execute_command(client, "docker ps", "Список запущенных контейнеров")
        
        # Проверяем Temporal
        print("\n=== Проверка Temporal ===")
        execute_command(client,
            "cd /root/shannon && docker-compose exec -T temporal temporal operator cluster health --address localhost:7233 2>&1 || echo 'Temporal не запущен'",
            "Здоровье Temporal")
        
        print("\n" + "=" * 60)
        print("[OK] Тест завершен!")
        print("=" * 60)
        print("\nShannon должен быть запущен.")
        print("Проверьте статус:")
        print("  ssh root@72.56.79.153")
        print("  cd /root/shannon")
        print("  docker ps")
        print("  ./shannon query ID=<workflow-id>")
        print("\nВеб-интерфейс: http://72.56.79.153:8233")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_shannon_with_key()

