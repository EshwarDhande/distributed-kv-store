#!/bin/bash

NUM_REQUESTS=10000
CONCURRENT_CLIENTS=50
SERVER_ADDRESS="localhost:50051"

echo "Starting load test with $NUM_REQUESTS requests and $CONCURRENT_CLIENTS concurrent clients..."

time seq $NUM_REQUESTS | xargs -P $CONCURRENT_CLIENTS -I {} python -c "
import grpc
import kvstore_pb2
import kvstore_pb2_grpc
stub = kvstore_pb2_grpc.KeyValueStoreStub(grpc.insecure_channel('$SERVER_ADDRESS'))
stub.Put(kvstore_pb2.KeyValue(key=f'key{{}}', value=f'value{{}}'))"

echo "Load test completed."
