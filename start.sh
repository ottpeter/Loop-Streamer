#!/bin/sh
script='/app/main.py /app/'

# Remove locks
/usr/bin/python3 /app/remove_locks.py
echo "Starting nginx..."
/usr/local/nginx/sbin/nginx &
echo "Starting main.py"
/usr/bin/python3 $script

while true
do

  # Remove locks
  /usr/bin/python3 /app/remove_locks.py
  echo "main.py has stopped."
  echo "Restarting main.py..."
  /usr/bin/python3 $script
  sleep 1
done
