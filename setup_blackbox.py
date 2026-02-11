#!/usr/bin/env python3
"""Create blackbox stub repo on server and optionally run pentest."""
import paramiko
import sys

HOST, USER, PASS = '72.56.79.153', 'root', 'm8J@2_6whwza6U'

def run(client, cmd):
    _, out, err = client.exec_command(cmd)
    return out.read().decode('utf-8', errors='replace') + err.read().decode('utf-8', errors='replace')

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://example.com'
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, port=22, timeout=15)

    run(client, 'mkdir -p /root/shannon/repos/blackbox')
    run(client, '''echo '# Black-Box Pentest Target
No source code available. External scans + browser recon only.' > /root/shannon/repos/blackbox/README.md''')
    run(client, 'cd /root/shannon/repos/blackbox && git init && git add . && git commit -m "Black-box stub" 2>/dev/null || true')

    print(f"Blackbox stub ready. Start pentest with:")
    print(f"  ./shannon start URL={url} REPO=/root/shannon/repos/blackbox")
    print("\nOr run now? (script would need to exec the start command)")

    client.close()

if __name__ == '__main__':
    main()
