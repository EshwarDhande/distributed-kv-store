import grpc
from concurrent import futures
import kvstore_pb2
import kvstore_pb2_grpc
from multiproc_worker import MultiprocessWorker
from replication import ReplicationManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PEER_SERVERS = ["localhost:50052", "localhost:50053"]  # List of peer servers

class KeyValueStoreServicer(kvstore_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.worker = MultiprocessWorker(num_workers=4)  # Multiprocessing support
        self.replication_manager = ReplicationManager(PEER_SERVERS)  # Enable replication

    def Put(self, request, context):
        """PUT operation with replication and multiprocessing."""
        old_value = self.worker.get(request.key)  # Get old value before updating
        self.worker.put(request.key, request.value)
        self.replication_manager.replicate_put(request.key, request.value)
        logging.info(f"PUT request processed: key={request.key}, value={request.value}")
        return kvstore_pb2.OldValue(old_value=old_value if old_value else "")

    def Get(self, request, context):
        """GET operation."""
        value = self.worker.get(request.key)
        if value:
            logging.info(f"GET request successful: key={request.key}, value={value}")
            return kvstore_pb2.Value(value=value)
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Key not found")
        logging.warning(f"GET request failed: key={request.key} not found")
        return kvstore_pb2.Value()

    def Delete(self, request, context):
        """DELETE operation with replication."""
        self.worker.delete(request.key)
        self.replication_manager.replicate_delete(request.key)
        logging.info(f"DELETE request processed: key={request.key}")
        return kvstore_pb2.Empty()

    def ListKeys(self, request, context):
        """LIST operation."""
        keys = self.worker.get_all_keys()
        logging.info(f"LIST request processed: keys={keys}")
        return kvstore_pb2.KeyList(keys=keys)

    def Backup(self, request, context):
        """Backup operation using multiprocessing."""
        logging.info("Initiating Backup...")
        self.worker.backup()
        return kvstore_pb2.BackupStatus(success=True, message="Backup started in background.")


def serve():
    """Starts the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kvstore_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    logging.info("🚀 gRPC Server started on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
