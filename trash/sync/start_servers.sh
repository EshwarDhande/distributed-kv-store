#!/bin/bash

NUM_SERVERS=3
BASE_PORT=50051

# Stop any existing servers first
echo "🔴 Stopping old servers..."
pkill -f multiproc_server.py

# Wait a bit for cleanup
sleep 2

# Start new servers
echo "🚀 Starting $NUM_SERVERS gRPC servers..."
for i in $(seq 0 $(($NUM_SERVERS - 1)))
do
    PORT=$(($BASE_PORT + $i))

    # Ensure process isn't already running
    if ! lsof -i :$PORT > /dev/null 2>&1; then
        echo "🟢 Starting server on port $PORT..."
        nohup python server/multiproc_server.py --port=$PORT > logs/server_$PORT.log 2>&1 &
        sleep 2  # Ensure each server starts properly
    else
        echo "⚠️ Server on port $PORT is already running. Skipping..."
    fi
done

echo "✅ All servers started successfully!"
