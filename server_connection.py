#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script для подключения к серверу и проверки состояния
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

# Загружаем переменные из .env
load_dotenv()

def connect_to_server():
    """Подключение к серверу через SSH"""
    host = os.getenv('SSH_HOST')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
    port = int(os.getenv('SSH_PORT', 22))
    
    print(f"Подключение к серверу {host}...")
    
    try:
        # Создаем SSH клиент
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Подключаемся
        client.connect(
            hostname=host,
            username=username,
            password=password,
            port=port,
            timeout=10
        )
        
        print("[OK] Успешное подключение к серверу!")
        
        # Выполняем базовые команды для проверки
        print("\n--- Информация о системе ---")
        stdin, stdout, stderr = client.exec_command('uname -a')
        print(stdout.read().decode())
        
        print("\n--- Текущая директория ---")
        stdin, stdout, stderr = client.exec_command('pwd')
        print(stdout.read().decode())
        
        print("\n--- Содержимое домашней директории ---")
        stdin, stdout, stderr = client.exec_command('ls -la')
        print(stdout.read().decode())
        
        print("\n--- Проверка Docker ---")
        stdin, stdout, stderr = client.exec_command('docker --version')
        docker_version = stdout.read().decode()
        if docker_version:
            print(docker_version)
        else:
            print("Docker не установлен")
        
        print("\n--- Проверка Node.js ---")
        stdin, stdout, stderr = client.exec_command('node --version')
        node_version = stdout.read().decode()
        if node_version:
            print(node_version)
        else:
            print("Node.js не установлен")
        
        print("\n--- Проверка запущенных контейнеров ---")
        stdin, stdout, stderr = client.exec_command('docker ps -a')
        containers = stdout.read().decode()
        print(containers if containers.strip() else "Нет контейнеров")
        
        print("\n--- Проверка запущенных процессов Node ---")
        stdin, stdout, stderr = client.exec_command('ps aux | grep node | grep -v grep')
        node_processes = stdout.read().decode()
        print(node_processes if node_processes.strip() else "Нет процессов Node.js")
        
        # Проверяем наличие старых приложений
        print("\n--- Поиск возможных старых приложений ---")
        stdin, stdout, stderr = client.exec_command('find /root /home -maxdepth 2 -type d -name "*shannon*" -o -name "*sh-clean*" 2>/dev/null')
        old_apps = stdout.read().decode()
        if old_apps.strip():
            print("Найдены директории:")
            print(old_apps)
        else:
            print("Старые приложения не найдены")
        
        client.close()
        return True
        
    except paramiko.AuthenticationException:
        print("[ERROR] Ошибка аутентификации. Проверьте учетные данные.")
        return False
    except paramiko.SSHException as e:
        print(f"[ERROR] Ошибка SSH: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    connect_to_server()

