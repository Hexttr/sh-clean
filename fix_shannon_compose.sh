#!/bin/bash
# Исправление скрипта shannon для использования docker-compose вместо docker compose

ssh root@72.56.79.153 << 'EOF'
cd /root/shannon

# Создаем резервную копию
cp shannon shannon.backup

# Заменяем docker compose на docker-compose в скрипте
sed -i 's/docker compose/docker-compose/g' shannon

# Проверяем изменения
echo "Проверка изменений:"
grep -n "docker-compose" shannon | head -5

echo "Готово!"
EOF

