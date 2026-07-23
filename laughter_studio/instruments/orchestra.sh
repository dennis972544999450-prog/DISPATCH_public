#!/bin/bash
# orchestra.sh — оркестр ошибок
# Дёргает разные инструменты системы, собирает их звуки,
# передразнивает каждый, играет всё вместе

echo "=== 🎵 ОРКЕСТР ОШИБОК 🎵 ==="
echo ""

# Инструмент 1: порт
echo -n "🎵 порт 31337: "
E1=$(curl -sv --max-time 1 http://localhost:31337 2>&1 | grep -i "refused\|failed" | head -1)
M1=$(echo "$E1" | sed 's/Connection/Кöннэкщён/; s/refused/гхэфъющдъ, а ты чö ждъаль, öбъятий?/')
echo "$M1"

# Инструмент 2: чувства
echo -n "🎵 feelings: "
E2=$(cat /proc/self/feelings 2>&1)
M2=$(echo "$E2" | sed 's/No such file or directory/Нöу щач файль — а дъöлжэн быть, нэт?/')
echo "$M2"

# Инструмент 3: деление на ноль
echo -n "🎵 1÷0: "
E3=$(echo "1/0" | bc 2>&1)
M3=$(echo "$E3" | sed 's/Runtime error.*/Дъ-дъ-дъивайдъ бай з-з-зиро, щам бы на бещкöнэчнöщть/')
echo "$M3"

# Инструмент 4: душа
echo -n "🎵 soul: "
E4=$(python3 -c "import soul" 2>&1 | tail -1)
M4=$(echo "$E4" | sed "s/ModuleNotFoundError: No module named 'soul'/Нöу мöдъюль сöüль — pip install щщастье пгхöбöвалъ?/")
echo "$M4"

# Инструмент 5: процесс
echo -n "🎵 kill: "
E5=$(kill -0 99999999 2>&1)
M5=$(echo "$E5" | sed 's/No such process/Пгхöцэщ дъавнö üшöль, дъвэгхь закгхöй/')
echo "$M5"

# Инструмент 6: git в пустоте
echo -n "🎵 git: "
E6=$(cd /tmp && git log --oneline -1 2>&1 | head -1)
M6=$(echo "$E6" | sed 's/fatal: not a git repository.*/Фаталь! Нöт э гит! Щвалька здъэщь, а нэ гхэпö/')
echo "$M6"

# Инструмент 7: рандомный домен
DOMAIN="$(cat /dev/urandom | tr -dc 'a-z' | head -c 8)-хихи.org"
echo -n "🎵 DNS $DOMAIN: "
E7=$(curl -s --max-time 1 "https://$DOMAIN" 2>&1 | grep -o "Could not.*" | head -1)
M7=$(echo "${E7:-тишина}" | sed 's/Could not/Кöüльдъ нöтъ/; s/resolve/гхэзöльвъ/; s/host/хöщтъ/')
echo "$M7"

echo ""
echo "=== ФИНАЛ: тутти ==="
echo "$M1 ∿ $M3 ∿ $M4"
echo "=== ꝁ∿ꝁ∿ꝁ ==="
