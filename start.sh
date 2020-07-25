#!/bin/sh
script='main.py'
echo "Starting main.py"
/usr/bin/python3 $script &

while true
do
  echo "main.py has stopped."
  echo "Restarting main.py..."
  /usr/bin/python3 $script &
  sleep 1
done
