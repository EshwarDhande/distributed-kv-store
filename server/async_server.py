import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import kvstore_pb2
from kvstore_pb2 import OldValue, Value, Empty, KeyList, BackupStatus
import kvstore_pb2_grpc
import grpc
import asyncio
import signal
import argparse  # Allow setting a custom port
import logging

from multiproc_worker import MultiprocessWorker  # Multiprocessing for parallel execution
from replication import ReplicationManager  # Replication support

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_peer_servers(port):
    """Return a list of peer servers excluding the current server's port."""
    all_ports = [50051, 50052, 50053]  # Define available server ports
    return [f"localhost:{p}" for p in all_ports if p != port]  # Exclude current port

class AsyncKeyValueStoreServicer(kvstore_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, port):
        self.worker = MultiprocessWorker()  # Use multiprocessing worker
        self.replication_manager = ReplicationManager(get_peer_servers(port))  # Dynamic peer selection
        logging.info(f"Server initialized on port {port} with peers: {get_peer_servers(port)}")

    async def Ping(self, request, context):
        """Health check method to verify server availability."""
        return kvstore_pb2.PingResponse(message="OK")
    
    async def Put(self, request, context):
        """Asynchronously store a key-value pair and replicate."""
        logging.info(f"PUT request received for key: {request.key}, value: {request.value}")
        old_value = await self.worker.get(request.key)
        await self.worker.put(request.key, request.value)
        asyncio.create_task(self.replication_manager.replicate_put(request.key, request.value))  
        return kvstore_pb2.OldValue(old_value=old_value if old_value else "")

    async def Get(self, request, context):
        """Retrieve a value asynchronously."""
        value = await self.worker.get(request.key)
        if value is None: 
                logging.info(f"Key '{request.key}' not found.")
                return kvstore_pb2.Value(value= "")  
        if not isinstance(value, str):  # Ensure it's a string
            logging.error(f"Invalid return type from worker.get(): {type(value).__name__}")
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Invalid data type returned")
            return kvstore_pb2.Value(value="")  # Return empty string instead of None
        return kvstore_pb2.Value(value=value)
    
    async def Delete(self, request, context):
        """Delete a key asynchronously and replicate delete operation."""
        logging.info(f"DELETE request received for key: {request.key}")
        success = await self.worker.delete(request.key) 
        if not success:
            logging.error(f"Failed to delete key: {request.key}")
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Key deletion failed")
            return Empty()
        asyncio.create_task(self.replication_manager.replicate_delete(request.key))
        return Empty()

    async def ListKeys(self, request, context):
        """Retrieve all stored keys asynchronously."""
        logging.info("LIST request received")
        keys = await self.worker.get_all_keys() 
        if not isinstance(keys, list):  # ✅ Ensure it's a list
            logging.error(f"Invalid return type from worker.get_all_keys(): {type(keys).__name__}")
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Invalid data type returned")
            return kvstore_pb2.KeyList(keys=[])
        # Ensure all keys are strings
        if not all(isinstance(k, str) for k in keys):
            logging.error(f"Invalid key types found in list: {[type(k).__name__ for k in keys]}")
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Invalid data type in key list")
            return kvstore_pb2.KeyList(keys=[])
        return kvstore_pb2.KeyList(keys=keys)

    async def Backup(self, request, context):
        """Handles the backup request asynchronously using a worker."""
        logging.info("Initiating Backup...")
        success = await self.worker.backup()
        if not success:
            logging.error("Backup operation failed")
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Backup failed")
            return BackupStatus(success=False, message="Backup failed.")
        return BackupStatus(success=True, message="Backup started in background.")

async def serve(port):
    """Starts the async gRPC server on a specified port."""
    server = grpc.aio.server()
    kvstore_pb2_grpc.add_KeyValueStoreServicer_to_server(AsyncKeyValueStoreServicer(port), server)
    server.add_insecure_port(f"127.0.0.1:{port}")  # Bind to specified port

    await server.start()
    logging.info(f"Async gRPC Server started on port {port}")

    stop_event = asyncio.Event()
    
    def shutdown():
        logging.info("Shutting down server gracefully...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    await stop_event.wait()
    await server.stop(0)
    logging.info("Server shutdown complete.")    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=50051, help="Port number for the server")
    args = parser.parse_args()

    asyncio.run(serve(args.port))  
