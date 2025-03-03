import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../server")))

import grpc
import kvstore_pb2
import kvstore_pb2_grpc


class KeyValueClient:
    def __init__(self, server_address="localhost:50051"):
        self.channel = grpc.insecure_channel(server_address)  # ✅ Use synchronous gRPC channel
        self.stub = kvstore_pb2_grpc.KeyValueStoreStub(self.channel)

    def put(self, key, value):
        """Synchronous PUT operation."""
        response = self.stub.Put(kvstore_pb2.KeyValue(key=key, value=value))
        return response.old_value

    def get(self, key):
        """Synchronous GET operation."""
        try:
            response = self.stub.Get(kvstore_pb2.Key(key=key))
            return response.value
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def delete(self, key):
        """Synchronous DELETE operation."""
        self.stub.Delete(kvstore_pb2.Key(key=key))

    def list_keys(self):
        """Synchronous LIST operation."""
        response = self.stub.ListKeys(kvstore_pb2.Empty())
        return response.keys

    def backup(self):
        """Synchronous BACKUP operation."""
        response = self.stub.Backup(kvstore_pb2.Empty())
        return response.success, response.message


def test_client():
    client = KeyValueClient()
    
    print("Putting key 'foo' -> 'bar'")
    old_value = client.put("foo", "bar")
    print(f"Old value: {old_value}")
    
    print("Getting key 'foo'")
    value = client.get("foo")
    print(f"Value: {value}")
    
    print("Listing keys")
    keys = client.list_keys()
    print(f"Keys: {keys}")
    
    print("Deleting key 'foo'")
    client.delete("foo")
    
    print("Creating backup")
    success, message = client.backup()
    print(f"Backup Status: {success}, Message: {message}")


# ✅ Testing Client
if __name__ == "__main__":
    test_client()
