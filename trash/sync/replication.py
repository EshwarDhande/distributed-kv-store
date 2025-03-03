import grpc
import time
import kvstore_pb2
import kvstore_pb2_grpc
import concurrent.futures

class ReplicationManager:
    def __init__(self, peers, max_retries=3):
        """Initialize with a list of peer addresses (host:port)."""
        self.peers = peers
        self.stubs = {peer: kvstore_pb2_grpc.KeyValueStoreStub(grpc.insecure_channel(peer)) for peer in peers}
        self.max_retries = max_retries  # Max retry attempts

    def _replicate_request(self, stub, method, request, peer):
        """Helper function to send a gRPC request with retries (synchronous)."""
        retry_delay = 1  # Initial delay in seconds
        for attempt in range(1, self.max_retries + 1):
            try:
                method(request)  # Synchronous gRPC call
                print(f"✅ Replication to {peer} succeeded.")
                return True  # Success
            except grpc.RpcError as e:
                print(f"⚠️ Replication attempt {attempt} to {peer} failed: {e.code().name}")
                if attempt < self.max_retries:
                    time.sleep(retry_delay)  # Blocking retry delay
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"❌ Failed to replicate to {peer} after {self.max_retries} attempts.")
                    return False  # Failure

    def replicate_put(self, key, value):
        """Send a synchronous PUT request to all peers in parallel."""
        request = kvstore_pb2.KeyValue(key=key, value=value)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self._replicate_request, stub, stub.Put, request, peer) 
                       for peer, stub in self.stubs.items()}
            concurrent.futures.wait(futures)

    def replicate_delete(self, key):
        """Send a synchronous DELETE request to all peers in parallel."""
        request = kvstore_pb2.Key(key=key)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self._replicate_request, stub, stub.Delete, request, peer) 
                       for peer, stub in self.stubs.items()}
            concurrent.futures.wait(futures)


# ✅ Testing Replication
if __name__ == "__main__":
    peers = ["localhost:50052", "localhost:50053"]
    replicator = ReplicationManager(peers)

    print("Replicating PUT foo -> bar")
    replicator.replicate_put("foo", "bar")

    print("Replicating DELETE foo")
    replicator.replicate_delete("foo")
