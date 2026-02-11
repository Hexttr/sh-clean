#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка статуса Shannon на сервере и доступности целей для пентеста
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

# Credentials (from .env or defaults)
SSH_HOST = os.getenv('SSH_HOST', '72.56.79.153')
SSH_USER = os.getenv('SSH_USER', 'root')
SSH_PASSWORD = os.getenv('SSH_PASSWORD', 'm8J@2_6whwza6U')
SSH_PORT = int(os.getenv('SSH_PORT', 22))

def run_cmd(client, cmd, silent=False):
    """Execute command and return (success, output)"""
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if not silent and (out or err):
        print(out)
        if err:
            print(err, file=sys.stderr)
    return exit_status == 0, out.strip()

def check_server():
    """Full server status check"""
    print("=" * 70)
    print("  ПРОВЕРКА СТАТУСА SHANNON НА СЕРВЕРЕ")
    print("=" * 70)
    print(f"\nСервер: {SSH_HOST}:{SSH_PORT}")
    print(f"Пользователь: {SSH_USER}")
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=SSH_HOST,
            username=SSH_USER,
            password=SSH_PASSWORD,
            port=SSH_PORT,
            timeout=15
        )
        print("\n[OK] SSH подключение успешно\n")
        
        # 1. Docker status
        print("-" * 70)
        print("1. DOCKER")
        print("-" * 70)
        ok, out = run_cmd(client, "docker --version")
        if ok:
            print(f"[OK] {out}")
        else:
            print("[ERROR] Docker не установлен или недоступен")
        
        # 2. Shannon containers
        print("\n" + "-" * 70)
        print("2. КОНТЕЙНЕРЫ SHANNON")
        print("-" * 70)
        ok, out = run_cmd(client, "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'shannon|temporal|NAMES'")
        if ok and out:
            print(out)
        else:
            ok, out = run_cmd(client, "docker ps -a 2>&1")
            if 'temporal' in out or 'worker' in out:
                for line in out.split('\n'):
                    if 'temporal' in line or 'worker' in line or 'NAMES' in line:
                        print(line)
            else:
                print("[INFO] Контейнеры Shannon не найдены. Возможно, Shannon не запущен.")
        
        # 3. Check if Shannon directory exists
        print("\n" + "-" * 70)
        print("3. ДИРЕКТОРИЯ SHANNON")
        print("-" * 70)
        ok, out = run_cmd(client, "ls -la /root/shannon 2>&1 | head -15")
        if ok:
            print("[OK] /root/shannon существует")
            run_cmd(client, "ls /root/shannon/")
        else:
            print("[ERROR] /root/shannon не найдена")
        
        # 4. Check ports and services
        print("\n" + "-" * 70)
        print("4. ДОСТУПНЫЕ СЕРВИСЫ И ПОРТЫ")
        print("-" * 70)
        
        # Temporal Web UI
        ok, _ = run_cmd(client, "curl -s -o /dev/null -w '%{http_code}' http://localhost:8233 2>/dev/null || echo '000'", silent=True)
        run_cmd(client, "curl -s -o /dev/null -w 'Temporal Web UI (8233): HTTP %{http_code}' http://localhost:8233 2>/dev/null; echo")
        
        # Juice Shop
        ok, code = run_cmd(client, "curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 2>/dev/null || echo '000'", silent=True)
        if code and code != '000':
            print(f"[OK] Juice Shop (3001): HTTP {code} - ДОСТУПЕН")
        else:
            print("[INFO] Juice Shop (3001): недоступен или не запущен")
        
        # Check host.docker.internal / host network - for containers
        run_cmd(client, "ss -tlnp 2>/dev/null | grep -E '3001|8233|7233' || netstat -tlnp 2>/dev/null | grep -E '3001|8233|7233' || true")
        
        # 5. API key
        print("\n" + "-" * 70)
        print("5. КОНФИГУРАЦИЯ API")
        print("-" * 70)
        ok, out = run_cmd(client, "test -f /root/shannon/.env && grep -c 'ANTHROPIC_API_KEY=' /root/shannon/.env 2>/dev/null | grep -v '^0$' && echo 'OK' || echo 'NOT_SET'", silent=True)
        run_cmd(client, "test -f /root/shannon/.env && grep 'ANTHROPIC_API_KEY=' /root/shannon/.env | sed 's/=.*/=***/' || echo '.env не найден'")
        
        # 6. Audit logs / completed runs
        print("\n" + "-" * 70)
        print("6. ПРОШЕДШИЕ ПЕНТЕСТЫ")
        print("-" * 70)
        ok, out = run_cmd(client, "ls -la /root/shannon/audit-logs/ 2>/dev/null | head -20")
        if out and 'total' in out:
            print(out)
        else:
            print("[INFO] audit-logs пуста или не существует")
        
        # 7. Repos available for pentest
        print("\n" + "-" * 70)
        print("7. РЕПОЗИТОРИИ ДЛЯ ПЕНТЕСТА")
        print("-" * 70)
        ok, out = run_cmd(client, "ls -la /root/shannon/repos/ 2>/dev/null")
        run_cmd(client, "ls -la /root/shannon/repos/ 2>/dev/null")
        
        # 8. Juice Shop - is it running in Docker?
        print("\n" + "-" * 70)
        print("8. JUICE SHOP (цель для пентеста)")
        print("-" * 70)
        ok, out = run_cmd(client, "docker ps | grep -i juice 2>/dev/null || docker ps -a | grep -i juice 2>/dev/null || echo 'Juice Shop container not found'")
        if 'juice' in out.lower():
            print(out)
        else:
            print("[INFO] Juice Shop не запущен в Docker")
            print("      Для пентеста Juice Shop нужно: docker run -d -p 3001:3000 bkimminich/juice-shop")
        
        client.close()
        
        # Summary
        print("\n" + "=" * 70)
        print("  РЕЗЮМЕ И АДРЕСА ДЛЯ ПЕНТЕСТА")
        print("=" * 70)
        print(f"""
  Temporal Web UI (мониторинг):  http://{SSH_HOST}:8233
  
  Для пентеста Shannon нужен URL целевого приложения.
  Worker контейнер Shannon обращается к целям по сети.
  
  Если Juice Shop запущен на хосте (localhost:3001):
    -> Worker должен использовать: http://host.docker.internal:3001
    -> Или: http://172.17.0.1:3001 (Docker bridge)
  
  Если Juice Shop НЕ запущен:
    1. Запустите: docker run -d -p 3001:3000 bkimminich/juice-shop
    2. Пентест: ./shannon start URL=http://host.docker.internal:3001 REPO=/root/shannon/repos/juice-shop
  
  Публичный доступ к Juice Shop (если порт открыт):
    -> http://{SSH_HOST}:3001
""")
        print("=" * 70)
        return True
        
    except paramiko.AuthenticationException as e:
        print(f"[ERROR] Ошибка аутентификации: {e}")
        return False
    except paramiko.SSHException as e:
        print(f"[ERROR] SSH ошибка: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_server()
