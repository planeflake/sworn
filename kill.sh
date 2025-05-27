#!/bin/bash

PORT=8000

echo "🔍 Searching for process using port $PORT..."
PID=$(lsof -ti tcp:$PORT)

if [ -z "$PID" ]; then
  echo "✅ No process found using port $PORT."
else
  echo "🛑 Killing process $PID using port $PORT..."
  kill -9 $PID
  if [ $? -eq 0 ]; then
    echo "✅ Process $PID terminated successfully."
  else
    echo "❌ Failed to kill process $PID."
  fi
fi
