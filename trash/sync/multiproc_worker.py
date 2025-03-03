# import multiprocessing
# import threading
# import lmdb

# class MultiprocessWorker:
#     """Manages database operations using a single process with worker threads."""
#     def __init__(self, db_path="kvstore.lmdb", num_threads=4):
#         self.task_queue = multiprocessing.Queue()
#         self.result_queue = multiprocessing.Queue()
#         self.db_path = db_path
#         self.num_threads = num_threads
#         self.threads = []

#         # ✅ Use threads instead of multiple processes
#         for _ in range(self.num_threads):
#             thread = threading.Thread(target=self._worker)
#             thread.daemon = True
#             thread.start()
#             self.threads.append(thread)

#     def _worker(self):
#         """Thread worker function to process tasks."""
#         db_env = lmdb.open(self.db_path, map_size=10485760, max_dbs=1)
#         while True:
#             task = self.task_queue.get()
#             if task is None:
#                 break

#             operation, key, value = task
#             try:
#                 with db_env.begin(write=True) as txn:
#                     if operation == "put":
#                         txn.put(key.encode(), value.encode())
#                         self.result_queue.put(f"Put {key} -> {value}")
#                     elif operation == "get":
#                         result = txn.get(key.encode())
#                         self.result_queue.put(result.decode() if result else None)
#                     elif operation == "delete":
#                         txn.delete(key.encode())
#                         self.result_queue.put(f"Deleted {key}")
#                     elif operation == "list_keys":
#                         with txn.cursor() as cursor:
#                             keys = [key.decode() for key, _ in cursor]
#                         self.result_queue.put(keys)
#                     elif operation == "backup":
#                         backup_path = "lmdb_backup"
#                         db_env.copy(backup_path, compact=True)
#                         self.result_queue.put(f"Backup successful -> {backup_path}")
#             except Exception as e:
#                 self.result_queue.put(f"Error: {str(e)}")

#     def put(self, key, value):
#         """Queue a PUT request."""
#         self.task_queue.put(("put", key, value))

#     def get(self, key):
#         """Queue a GET request and return result."""
#         self.task_queue.put(("get", key, None))
#         return self.result_queue.get()

#     def delete(self, key):
#         """Queue a DELETE request."""
#         self.task_queue.put(("delete", key, None))

#     def get_all_keys(self):
#         """Queue a LIST_KEYS request and return result."""
#         self.task_queue.put(("list_keys", None, None))
#         return self.result_queue.get()

#     def backup(self):
#         """Queue a BACKUP request."""
#         self.task_queue.put(("backup", None, None))
#         return self.result_queue.get()

#     def close(self):
#         """Stop all threads and cleanup."""
#         for _ in self.threads:
#             self.task_queue.put(None)
#         for thread in self.threads:
#             thread.join()



# Threads above are used to handle database operations synchronously.
#The following code snippet demonstrates how to use the MultiprocessWorker class:

import multiprocessing
import lmdb
import time
import shutil
import os

class WorkerProcess(multiprocessing.Process):
    """Worker process that handles database operations synchronously."""
    def __init__(self, task_queue, result_queue, db_path="kvstore.lmdb"):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.db_path = db_path

    def run(self):
        """Worker process main loop."""
        db_env = lmdb.open(self.db_path, map_size=10485760, max_dbs=1)  # Open DB per worker
        while True:
            task = self.task_queue.get()
            if task is None:
                break  # Exit signal received

            operation, key, value = task
            try:
                with db_env.begin(write=True) as txn:
                    if operation == "put":
                        txn.put(key.encode(), value.encode())
                        self.result_queue.put(f"Put {key} -> {value}")

                    elif operation == "get":
                        result = txn.get(key.encode())
                        self.result_queue.put(result.decode() if result else None)

                    elif operation == "delete":
                        txn.delete(key.encode())
                        self.result_queue.put(f"Deleted {key}")

                    elif operation == "list_keys":
                        with txn.cursor() as cursor:
                            keys = [key.decode() for key, _ in cursor]  # ✅ Ensure decoding
                        self.result_queue.put(keys)

                    elif operation == "backup":
                        backup_path = "lmdb_backup"
                        os.makedirs(backup_path, exist_ok=True)
                        db_env.copy(backup_path, compact=True)
                        self.result_queue.put(f"Backup successful -> {backup_path}")

            except Exception as e:
                self.result_queue.put(f"Error: {str(e)}")


class MultiprocessWorker:
    """Manager for spawning worker processes to handle database operations."""
    #def __init__(self, num_workers=4):
    def __init__(self, db_path="kvstore.lmdb"):
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        # self.workers = [WorkerProcess(self.task_queue, self.result_queue) for _ in range(num_workers)]

        # for worker in self.workers:
        #     worker.start()
        self.worker = WorkerProcess(self.task_queue, self.result_queue, db_path)
        self.worker.start()  # ✅ Start a single worker process

    def put(self, key, value):
        """Send a put request to workers (sync)."""
        self.task_queue.put(("put", key, value))
        return self.result_queue.get()  # ✅ Ensure we receive confirmation

    def get(self, key):
        """Send a get request to workers and wait for the result."""
        self.task_queue.put(("get", key, None))
        return self.result_queue.get()  # ✅ Ensure synchronous result retrieval

    def delete(self, key):
        """Send a delete request to workers."""
        self.task_queue.put(("delete", key, None))
        return self.result_queue.get()  # ✅ Ensure confirmation

    def get_all_keys(self):
        """Retrieve all stored keys synchronously."""
        self.task_queue.put(("list_keys", None, None))
        return self.result_queue.get()  # ✅ Ensure synchronous retrieval

    def backup(self):
        """Trigger a database backup synchronously."""
        self.task_queue.put(("backup", None, None))
        return self.result_queue.get()  # ✅ Ensure confirmation

    def close(self):
        """Gracefully shutdown worker processes."""
        for _ in self.workers:
            self.task_queue.put(None)  # Send exit signal

        for worker in self.workers:
            worker.join()


# ✅ Testing Multiprocessing
if __name__ == "__main__":
    worker = MultiprocessWorker()
    
    print("Putting key 'foo' -> 'bar'")
    print(worker.put("foo", "bar"))

    print("Getting key 'foo'")
    print(f"Value: {worker.get('foo')}")

    print("Listing all keys")
    print(f"Keys: {worker.get_all_keys()}")

    print("Creating backup")
    print(worker.backup())

    print("Deleting key 'foo'")
    print(worker.delete("foo"))

    worker.close()
