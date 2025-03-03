import asyncio
import threading
import queue
import lmdb
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MultiprocessWorker:
    """Manages database operations using threads with an async interface."""

    def __init__(self, db_path="kvstore.lmdb", num_threads=4):
        self.task_queue = queue.Queue()  # Blocking queue for thread communication
        self.result_queue = queue.Queue()
        self.db_path = db_path
        self.threads = []
        self.running = True

        # Start worker threads
        for _ in range(num_threads):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            self.threads.append(thread)

    def _worker(self):
        """Worker function to process database operations."""
        
        db_env = lmdb.open(self.db_path, map_size=10485760, max_dbs=1)

        while self.running:
            try:
                task = self.task_queue.get()
                if task is None:
                    break  # Stop signal received

                operation, key, value = task
                with db_env.begin(write=True) as txn:
                    if operation == "put":
                        old_value = txn.get(key.encode())  # Fetch old value before overwriting
                        txn.put(key.encode(), value.encode())  
                        self.result_queue.put(old_value.decode() if old_value else "")  # Return empty string if key doesn't exist
                    elif operation == "get":
                        result = txn.get(key.encode())
                        self.result_queue.put(result.decode() if result else "")  
                    elif operation == "delete":
                        txn.delete(key.encode())
                        self.result_queue.put(f"Deleted {key}")
                    elif operation == "list_keys":
                        with txn.cursor() as cursor:
                            keys = [key.decode() for key, _ in cursor]
                        self.result_queue.put(keys)
                    elif operation == "backup":
                        backup_path = "lmdb_backup"
                        db_env.copy(backup_path, compact=True)
                        self.result_queue.put(f"Backup successful -> {backup_path}")

            except Exception as e:
                logging.error(f"Database operation error: {e}")
                self.result_queue.put(f"Error: {str(e)}")

    async def put(self, key, value):
        """Queue a PUT request asynchronously and return only the stored value."""

        await asyncio.to_thread(self.task_queue.put, ("put", key, value))
        old_value = await asyncio.to_thread(self.result_queue.get)  #  Wait for the correct value
        logging.info(f"Put operation stored '{old_value}' for key '{key}'")  
        return old_value  

    async def get(self, key):
        """Queue a GET request asynchronously and return result."""

        await asyncio.to_thread(self.task_queue.put, ("get", key, None))
        value = await asyncio.to_thread(self.result_queue.get)
        logging.info(f" DEBUG: get() returned '{value}' for key '{key}'")  
        return value  
    
    async def delete(self, key):
        """Queue a DELETE request asynchronously."""

        await asyncio.to_thread(self.task_queue.put, ("delete", key, None))
        return await asyncio.to_thread(self.result_queue.get)


    async def get_all_keys(self):
        """Queue a LIST_KEYS request asynchronously and return result."""

        await asyncio.to_thread(self.task_queue.put, ("list_keys", None, None))
        result = await asyncio.to_thread(self.result_queue.get)

        if not isinstance(result, list):  # Ensure it's a list
            logging.error(f"Unexpected type in get_all_keys(): {type(result).__name__}, value={result}")
            return []

        # Ensure all items in the list are strings
        if not all(isinstance(k, str) for k in result):
            logging.error(f"Invalid key types found: {[type(k).__name__ for k in result]}")
            return []

        return result

    async def backup(self):
        """Queue a BACKUP request asynchronously."""

        await asyncio.to_thread(self.task_queue.put, ("backup", None, None))
        return await asyncio.to_thread(self.result_queue.get)

    async def close(self):
        """Stop all threads and cleanup."""

        self.running = False
        for _ in self.threads:
            await asyncio.to_thread(self.task_queue.put, None)  # Stop signal
        for thread in self.threads:
            thread.join()
        logging.info("Worker shut down gracefully.")

# Testing Asynchronous Thread Worker
async def test_async_worker():
    worker = MultiprocessWorker()

    logging.info("Putting key 'foo' -> 'bar'")
    await worker.put("foo", "bar")

    logging.info("Getting key 'foo'")
    value = await worker.get("foo")
    print(f"Value: {value}")

    logging.info("Listing all keys")
    keys = await worker.get_all_keys()
    print(f"Keys: {keys}")

    logging.info("Creating backup")
    backup_status = await worker.backup()
    print(f"Backup Status: {backup_status}")

    logging.info("Deleting key 'foo'")
    await worker.delete("foo")

    await worker.close()

if __name__ == "__main__":
    asyncio.run(test_async_worker())
