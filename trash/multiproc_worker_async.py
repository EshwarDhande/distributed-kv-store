import asyncio
import multiprocessing
import lmdb
import time

class WorkerProcess(multiprocessing.Process):
    """Worker process that handles database operations safely."""
    def __init__(self, task_queue, result_queue, db_path="kvstore.lmdb"):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.db_path = db_path

    def run(self):
        """Worker process main loop."""
        db_env = lmdb.open(self.db_path, map_size=10485760, max_dbs=1)
        while True:
            task = self.task_queue.get()
            if task is None:
                break  # Exit signal received

            operation, key, value = task
            try:
                with db_env.begin(write=True) as txn:
                    if operation == "put":
                        txn.put(key.encode(), value.encode())
                        self.result_queue.put((key, f"Put {key} -> {value}"))
                    elif operation == "get":
                        result = txn.get(key.encode())
                        self.result_queue.put((key, result.decode() if result else None))
                    elif operation == "delete":
                        txn.delete(key.encode())
                        self.result_queue.put((key, f"Deleted {key}"))
                    elif operation == "list_keys":
                        with txn.cursor() as cursor:
                            keys = [key.decode() for key, _ in cursor]
                        self.result_queue.put(("list_keys", keys))
                    elif operation == "backup":
                        backup_path = "lmdb_backup"
                        db_env.copy(backup_path, compact=True)
                        self.result_queue.put(("backup", f"Backup successful -> {backup_path}"))
            except Exception as e:
                self.result_queue.put((key, f"Error: {str(e)}"))

class MultiprocessWorker:
    """Async wrapper for multiprocessing-based worker processes."""
    def __init__(self, num_workers=4):
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.workers = [WorkerProcess(self.task_queue, self.result_queue) for _ in range(num_workers)]

        for worker in self.workers:
            worker.start()

        # Async queue to store future results
        self.loop = asyncio.get_event_loop()
        self.pending_results = {}

        # Start an async task to fetch results
        self.loop.create_task(self._fetch_results())

    async def _fetch_results(self):
        """Polls the multiprocessing result queue and stores results asynchronously."""
        while True:
            result = await asyncio.to_thread(self.result_queue.get)
            key, value = result
            if key in self.pending_results:
                self.pending_results[key].set_result(value)

    async def put(self, key, value):
        """Send a put request asynchronously."""
        self.task_queue.put(("put", key, value))

    async def get(self, key):
        """Send a get request asynchronously and return result."""
        self.task_queue.put(("get", key, None))
        self.pending_results[key] = self.loop.create_future()
        return await self.pending_results[key]

    async def delete(self, key):
        """Send a delete request asynchronously."""
        self.task_queue.put(("delete", key, None))

    async def get_all_keys(self):
        """Retrieve all stored keys asynchronously."""
        self.task_queue.put(("list_keys", None, None))
        self.pending_results["list_keys"] = self.loop.create_future()
        return await self.pending_results["list_keys"]

    async def backup(self):
        """Trigger a database backup asynchronously."""
        self.task_queue.put(("backup", None, None))
        self.pending_results["backup"] = self.loop.create_future()
        return await self.pending_results["backup"]

    async def close(self):
        """Gracefully shutdown worker processes."""
        for _ in self.workers:
            self.task_queue.put(None)  # Send exit signal
        for worker in self.workers:
            worker.join()

# ✅ Testing Asynchronous Multiprocessing Worker
async def test_async_worker():
    worker = MultiprocessWorker()

    print("Putting key 'foo' -> 'bar'")
    await worker.put("foo", "bar")

    print("Getting key 'foo'")
    value = await worker.get("foo")
    print(f"Value: {value}")

    print("Listing all keys")
    keys = await worker.get_all_keys()
    print(f"Keys: {keys}")

    print("Creating backup")
    backup_status = await worker.backup()
    print(f"Backup Status: {backup_status}")

    print("Deleting key 'foo'")
    await worker.delete("foo")

    await worker.close()

if __name__ == "__main__":
    asyncio.run(test_async_worker())
