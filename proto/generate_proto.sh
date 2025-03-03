#!/bin/bash

# Define the output directories
PROTO_DIR="$(dirname "$0")"
SERVER_OUT_DIR="${PROTO_DIR}/../server"
CLIENT_OUT_DIR="${PROTO_DIR}/../client"

# Create the output directories if they don't exist
mkdir -p "$SERVER_OUT_DIR"
mkdir -p "$CLIENT_OUT_DIR"

# Compile the proto file for Python (outputs to both server and client)
python -m grpc_tools.protoc -I"$PROTO_DIR" \
    --python_out="$SERVER_OUT_DIR" --grpc_python_out="$SERVER_OUT_DIR" \
    --python_out="$CLIENT_OUT_DIR" --grpc_python_out="$CLIENT_OUT_DIR" \
    "$PROTO_DIR/kvstore.proto"

echo "✅ gRPC files generated successfully in:"
echo "   - $SERVER_OUT_DIR"
echo "   - $CLIENT_OUT_DIR"
