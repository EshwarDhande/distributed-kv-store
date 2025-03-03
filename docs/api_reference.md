# API Reference - Distributed Key-Value Store

## Overview
This document provides details about the gRPC API for interacting with the distributed key-value store.

## Service Definition

```proto
service KeyValueStore {
  rpc Put(KeyValue) returns (OldValue);
  rpc Get(Key) returns (Value);
  rpc Delete(Key) returns (Empty);
  rpc ListKeys(Empty) returns (KeyList);
  rpc Backup(Empty) returns (BackupStatus);
}
```

## Methods

### Put
**Request:**
```proto
message KeyValue {
  string key = 1;  // Max length: 128 bytes
  string value = 2;  // Max length: 2048 bytes
}
```
**Response:**
```proto
message OldValue {
  string old_value = 1;  // Previous value if exists
}
```
Stores a key-value pair, returning the previous value if it existed.

### Get
**Request:**
```proto
message Key {
  string key = 1;
}
```
**Response:**
```proto
message Value {
  string value = 1;
}
```
Retrieves the value for a given key. Returns an error if the key is not found.

### Delete
**Request:**
```proto
message Key {
  string key = 1;
}
```
**Response:**
```proto
message Empty {}
```
Removes a key from the store.

### ListKeys
**Request:**
```proto
message Empty {}
```
**Response:**
```proto
message KeyList {
  repeated string keys = 1;
}
```
Returns a list of all stored keys.

### Backup
**Request:**
```proto
message Empty {}
```
**Response:**
```proto
message BackupStatus {
  bool success = 1;
  string message = 2;
}
```
Creates a backup of the database, returning success status.

## Error Handling
- `NOT_FOUND`: Key does not exist.
- `INTERNAL`: Server encountered an unexpected issue.
- `UNAVAILABLE`: Server is not reachable.

## Example Usage (Python Client)
```python
import grpc
import kvstore_pb2
import kvstore_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = kvstore_pb2_grpc.KeyValueStoreStub(channel)

# Put a key-value pair
stub.Put(kvstore_pb2.KeyValue(key="test", value="hello"))

# Retrieve the value
response = stub.Get(kvstore_pb2.Key(key="test"))
print(response.value)  # Output: hello
```

## Notes
- All keys and values must be ASCII strings.
- Ensure gRPC services are running before making requests.

For further details, refer to the [Project README](../README.md).
