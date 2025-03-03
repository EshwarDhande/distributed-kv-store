import grpc
import kvstore_pb2
import kvstore_pb2_grpc
import asyncio
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ReplicationManager:
    """Manages replication to multiple peers. """

    def __init__(self, peers, max_retries=3):
        self.peers = peers # List of peer addresses
        self.max_retries = max_retries # Maximum number of retries
        self.stubs = {}  # Cached gRPC stubs for peer communication

    def _get_stub(self, peer):
        """Return a fresh stub if the connection is stale."""

        if peer not in self.stubs or self.stubs[peer]._channel._state != grpc.ChannelConnectivity.READY:
            self.stubs[peer] = kvstore_pb2_grpc.KeyValueStoreStub(grpc.aio.insecure_channel(peer))
        return self.stubs[peer]

    async def _replicate_request(self, method, request, peer):
        """Send gRPC request with retries and backoff."""

        retry_delay = 1     # Initial retry delay in seconds
        max_delay = 10      # Maximum delay between retries

        for attempt in range(1, self.max_retries + 1):
            try:
                stub = self._get_stub(peer)  # Get fresh stub if needed
                await asyncio.wait_for(method(request), timeout=3)
                logging.info(f" Replication to {peer} succeeded.")
                return True
            except (grpc.aio.AioRpcError, asyncio.TimeoutError) as e:
                logging.warning(f" Replication attempt {attempt}/{self.max_retries} to {peer} failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(min(retry_delay, max_delay))
                    retry_delay *= 2        # Exponential backoff
                else:
                    logging.error(f" Final failure: Could not replicate to {peer}.")
                    return False

    async def replicate_put(self, key, value):
        """Send a PUT request to all peers in parallel."""

        request = kvstore_pb2.KeyValue(key=key, value=value)
        tasks = [self._replicate_request(stub, stub.Put, request, peer) for peer, stub in self.stubs.items()]
        await asyncio.gather(*tasks)  #  Run replication tasks concurrently

    async def replicate_delete(self, key):
        """Send a DELETE request to all peers in parallel."""
        
        request = kvstore_pb2.Key(key=key)
        tasks = [self._replicate_request(stub, stub.Delete, request, peer) for peer, stub in self.stubs.items()]
        await asyncio.gather(*tasks)  #  Run replication tasks concurrently

# Testing Replication
if __name__ == "__main__":
    async def main():
        peers = ["localhost:50052", "localhost:50053"]
        replicator = ReplicationManager(peers)

        logging.info("Replicating PUT foo -> bar")
        await replicator.replicate_put("foo", "bar")

        logging.info("Replicating DELETE foo")
        await replicator.replicate_delete("foo")

    asyncio.run(main())  # Run async replication test
