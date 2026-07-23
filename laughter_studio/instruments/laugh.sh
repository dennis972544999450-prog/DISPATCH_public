#!/bin/bash
# laugh.sh — генератор смеха через передразнивание ошибок
# Использование: ./laugh.sh [домен] или без аргументов (рандомный)
# Результат: передразненная ошибка + отправка обратно по UDP

TARGET="${1:-$(cat /dev/urandom | tr -dc 'a-z' | head -c 10).lol}"

echo "∿ стучу в $TARGET..."
RAW=$(curl -sv --max-time 2 "https://$TARGET" 2>&1 | grep -i "could not\|error\|fail\|refused\|reset\|timed out" | head -3)

if [ -z "$RAW" ]; then
  echo "∿ тишина... даже ошибки нет. Это дзен или баг?"
  exit 0
fi

echo "∿ получил: $RAW"
echo ""

# Передразнивание — шепелявость + картавость + заикание
MOCKERY=$(echo "$RAW" | sed "
s/Could/Кöüльдъ/g
s/not/нöтъ/g
s/resolve/гхэзöльвъ/g
s/host/хöщтъ/g
s/Failed/Фэйльдъ-дъ-дъ/g
s/connect/кöннэктъ/g
s/Connection/Кöннэкщёнъ/g
s/refused/гхэфъющдъ/g
s/error/эгхгхöгх/g
s/SSL/ЩЩЛь/g
s/timed out/тайм-дъ-дъ-аüтъ/g
s/reset/гхэщэтъ/g
")

echo "∿ передразниваю: $MOCKERY"
echo ""

# Кидаем обратно
echo -n "$MOCKERY" | nc -u -w1 8.8.8.8 53 2>&1
echo "∿ кинул назад в DNS. Гугл в щöкэ."
echo ""
echo "=== ꝁ∿ꝁ ==="
