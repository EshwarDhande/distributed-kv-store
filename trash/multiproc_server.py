import grpc
import signal
import argparse  # Allow setting a custom port
from concurrent import futures
import kvstore_pb2
import kvstore_pb2_grpc
from multiproc_worker import MultiprocessWorker  # Multiprocessing for parallel execution
from replication import ReplicationManager  # Replication support

def get_peer_servers(port):
    """Return a list of peer servers excluding the current server's port."""
    all_ports = [50051, 50052, 50053]  # Define available server ports
    return [f"localhost:{p}" for p in all_ports if p != port]  # Exclude current port

class KeyValueStoreServicer(kvstore_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, port):
        self.worker = MultiprocessWorker()  # Use multiprocessing worker
        self.replication_manager = ReplicationManager(get_peer_servers(port))  # Dynamic peer selection

    def Put(self, request, context):
        """Store a key-value pair and replicate."""
        self.worker.put(request.key, request.value)  # Blocking write
        self.replication_manager.replicate_put(request.key, request.value)  # Replicate synchronously
        return kvstore_pb2.OldValue(old_value="")

    def Get(self, request, context):
        """Retrieve a value."""
        value = self.worker.get(request.key)  # Blocking read
        if value:
            return kvstore_pb2.Value(value=value)
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Key not found")
        return kvstore_pb2.Value()

    def Delete(self, request, context):
        """Delete a key and replicate delete operation."""
        self.worker.delete(request.key)  # Blocking delete
        self.replication_manager.replicate_delete(request.key)  # Replicate synchronously
        return kvstore_pb2.Empty()

    def ListKeys(self, request, context):
        """Retrieve all stored keys."""
        keys = self.worker.get_all_keys()  # Blocking operation
        return kvstore_pb2.KeyList(keys=keys)

    def Backup(self, request, context):
        """Handles the backup request."""
        print("🔄 Initiating Backup...")
        self.worker.backup()  # Blocking backup call
        return kvstore_pb2.BackupStatus(success=True, message="Backup completed successfully.")

def serve(port):
    """Starts the gRPC server on a specified port."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # Thread pool for concurrency
    kvstore_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(port), server)
    server.add_insecure_port(f"127.0.0.1:{port}")  # Bind to specified port

    server.start()
    print(f"🚀 Multiprocess gRPC Server started on port {port}")
    
    def shutdown(signum, frame):
        print("🛑 Shutting down server gracefully...")
        server.stop(0)
        exit(0)
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=50051, help="Port number for the server")
    args = parser.parse_args()
    serve(args.port)
