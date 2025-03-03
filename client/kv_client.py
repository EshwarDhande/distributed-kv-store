import sys
import os
import grpc

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../server")))

import kvstore_pb2
import kvstore_pb2_grpc
import asyncio
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class KeyValueClient:
    """
    A gRPC-based asynchronous client for interacting with a distributed key-value store.
    Supports key-value operations such as Put, Get, Delete, ListKeys, and Backup.

    """


    def __init__(self, server_list=None):
        """Initialize client with a list of servers."""
        self.servers = server_list if server_list else ["localhost:50051"]
        self.channel = None
        self.stub = None

    async def initialize(self):
        await self.kv_init(self.servers)  



    async def kv_init(self, server_list):
        """Initialize connection to the first available server."""
        if not server_list or not isinstance(server_list, list):
            logging.error("Invalid server list. Must be a list of 'host:port' strings.")
            return -1

        for server in server_list:
            try:
                logging.info(f"Trying to connect to {server}...")
                channel = grpc.aio.insecure_channel(server)
                stub = kvstore_pb2_grpc.KeyValueStoreStub(channel)

                # Verify connection with a test RPC (Ping)
                await stub.Ping(kvstore_pb2.PingRequest())
                
                self.channel = channel
                self.stub = stub
                logging.info(f"Connected to {server}")
                return 0  # Success

            except grpc.RpcError as e:
                logging.warning(f" Connection to {server} failed: {e.details()}")

        logging.error("No servers available. Initialization failed.")
        return -1  # Failure

    async def kv_shutdown(self):
        """Shutdown the gRPC connection asynchronously."""
        if self.channel:
            logging.info("Shutting down client connection...")
            await self.channel.close()  
            self.channel = None
            self.stub = None
            logging.info("Connection successfully closed.")
            return 0
        logging.warning("No active connection to shut down.")
        return -1  # Failure


    async def put(self, key, value):
        """Store a key-value pair in the key-value store."""
        if not self.stub:
            logging.error("Client not initialized.")
            return -1

        logging.info(f"Sending PUT request: {key} -> {value}")
        response = await self.stub.Put(kvstore_pb2.KeyValue(key=key, value=value))
        return response.old_value

    async def get(self, key):
        """Retrieve the value associated with a given key."""
        if not isinstance(key, str):
            raise TypeError(f"Expected 'key' as str, got {type(key).__name__}")

        if not self.stub:
            logging.error("Client not initialized.")
            return -1

        logging.info(f"Sending GET request for key: {key}")
        try:
            response = await self.stub.Get(kvstore_pb2.Key(key=key))
            return response.value
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                logging.warning(f"Key not found: {key}")
                return None
            raise

    async def delete(self, key):
        """Delete a key from the key-value store."""
        if not self.stub:
            logging.error("Client not initialized.")
            return -1

        logging.info(f"Sending DELETE request for key: {key}")
        await self.stub.Delete(kvstore_pb2.Key(key=key))

    async def list_keys(self):
        """Retrieve a list of all stored keys."""
        if not self.stub:
            logging.error("Client not initialized.")
            return -1
        
        logging.info("Sending LIST request")
        response = await self.stub.ListKeys(kvstore_pb2.Empty())
        return response.keys

    async def backup(self):
        """Trigger a backup of the key-value store."""
        if not self.stub:
            logging.error("Client not initialized.")
            return -1

        logging.info("Sending BACKUP request")
        response = await self.stub.Backup(kvstore_pb2.Empty())
        return response.success, response.message

async def test_client():
    """Test client operations to verify correctness."""
    client = KeyValueClient(["localhost:50051", "localhost:50052", "localhost:50053"])
    
    logging.info("Starting client test...")
    await client.kv_init(["localhost:50051", "localhost:50052"]) 
       
    logging.info("Putting key 'foo' -> 'bar'")
    old_value = await client.put("foo", "bar")
    logging.info(f"Old value: {old_value}")
    
    logging.info("Getting key 'foo'")
    value = await client.get("foo")
    logging.info(f"Value: {value}")
    
    logging.info("Listing keys")
    keys = await client.list_keys()
    logging.info(f"Keys: {keys}")
    
    logging.info("Deleting key 'foo'")
    await client.delete("foo")
    
    logging.info("Creating backup")
    success, message = await client.backup()
    logging.info(f"Backup Status: {success}, Message: {message}")

    await client.kv_shutdown()

if __name__ == "__main__":
    asyncio.run(test_client())

 