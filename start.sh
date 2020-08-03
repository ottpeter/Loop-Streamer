#!/bin/sh
script='/app/main.py /app/'
echo "Starting nginx..."
/usr/local/nginx/sbin/nginx &
echo "Starting main.py"
/usr/bin/python3 $script

while true
do
  echo "main.py has stopped."
  echo "Restarting main.py..."
  /usr/bin/python3 $script
  sleep 1
done
