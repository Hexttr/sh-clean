#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление скрипта shannon на сервере для использования docker-compose
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

def fix_shannon_script():
    """Исправление скрипта shannon на сервере"""
    host = os.getenv('SSH_HOST')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
    port = int(os.getenv('SSH_PORT', 22))
    
    print("Подключение к серверу...")
    
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
        
        # Читаем текущий скрипт
        print("\nЧтение скрипта shannon...")
        sftp = client.open_sftp()
        remote_file = sftp.file('/root/shannon/shannon', 'r')
        content = remote_file.read().decode('utf-8')
        remote_file.close()
        
        # Создаем резервную копию
        print("Создание резервной копии...")
        backup_file = sftp.file('/root/shannon/shannon.backup', 'w')
        backup_file.write(content.encode('utf-8'))
        backup_file.close()
        
        # Заменяем docker compose на docker-compose
        print("Замена 'docker compose' на 'docker-compose'...")
        fixed_content = content.replace('docker compose', 'docker-compose')
        
        # Записываем исправленный скрипт
        print("Запись исправленного скрипта...")
        remote_file = sftp.file('/root/shannon/shannon', 'w')
        remote_file.write(fixed_content.encode('utf-8'))
        remote_file.close()
        sftp.close()
        
        # Делаем скрипт исполняемым
        print("Установка прав на выполнение...")
        stdin, stdout, stderr = client.exec_command('chmod +x /root/shannon/shannon')
        stdout.read()
        
        # Проверяем изменения
        print("\nПроверка изменений:")
        stdin, stdout, stderr = client.exec_command('grep -n "docker-compose" /root/shannon/shannon | head -3')
        print(stdout.read().decode('utf-8'))
        
        print("\n[OK] Скрипт исправлен!")
        print("Резервная копия сохранена в: /root/shannon/shannon.backup")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_shannon_script()

