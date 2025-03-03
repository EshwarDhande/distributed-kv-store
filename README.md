# Distributed Key-Value Store

## Authors
- **Eshwar Dhande [23210038]**
- **Aamod Thakur [23210001]**

- **[Quick Report](/docs/616_prj1_report_slip1.pdf)**: `/docs/616_prj1_report_slip1.pdf`

## Overview
This project implements a distributed key-value store using a **shared-nothing architecture** with **gRPC-based communication**. The system supports multiple nodes, replication, and failure recovery, ensuring **eventual consistency** and optimized **performance** under different workloads.

## Features
- **Distributed Storage**: Multiple nodes handling key-value operations independently.
- **gRPC API**: Supports `Put`, `Get`, `Delete`, `ListKeys`, and `Backup` operations.
- **Replication & Consistency**: Uses replication to maintain eventual consistency.
- **Persistence**: Data stored in LMDB or RocksDB for durability.
- **Fault Tolerance**: Recovers from process failures while minimizing data loss.
- **Performance Optimized**: Benchmarking for throughput and latency.

## System Architecture
- **Client-Server Model**: Clients interact via `kv_client.py`, which provides an asynchronous gRPC-based client implementation. It handles server discovery, connection management, and communication with the key-value store. The client supports non-blocking operations for `Put`, `Get`, `Delete`, and `ListKeys`, ensuring efficient interaction with the distributed system.
- **Shared-Nothing Design**: No shared memory or file access; all communication is explicit. The system utilizes `multiproc_worker.py` to manage database operations asynchronously with a queue-based threading model, ensuring efficient parallel execution of read and write requests.
- **Asynchronous gRPC Server**: Handles multiple client requests concurrently using `async_server.py`, which implements an asynchronous gRPC server. This server leverages `asyncio` for non-blocking request handling, enabling efficient concurrency and high throughput.
- **Replication Manager**: Ensures data availability across nodes using `replication.py`. This module manages data synchronization between nodes, ensuring consistency through gRPC-based replication of key-value updates and deletions. It handles network partitions, retries failed replications, and ensures eventual consistency after node recovery.
- **Storage Backend**: LMDB for fast key-value operations, managed through `lmdb_store.py`. This module handles key-value storage, retrieval, deletion, and backup functionalities. It ensures durability by using transactional writes and efficient disk storage, supporting fast read and write operations while maintaining data integrity.

## Installation
### Prerequisites
- Ubuntu 22.04 LTS
- Python 3.8+
- `pip install -r requirements.txt`
- `grpcio`, `grpcio-tools`, `lmdb`, `pytest`

### Build and Run
1. **Generate gRPC Stubs:**
   ```sh
   bash proto/generate_proto.sh
   ```
2. **Start Servers:**
   ```sh
   bash scripts/start_servers.sh
   ```
3. **Run Client Tests:**
   ```sh
   python client/kv_client.py
   ```

## Usage
### Using the Python Client (`kv_client.py`)
```python
from client.kv_client import KeyValueClient
import asyncio

async def main():
    client = KeyValueClient(["localhost:50051", "localhost:50052"])
    await client.initialize()
    await client.put("key", "value")
    value = await client.get("key")
    print(f"Value: {value}")
    await client.kv_shutdown()

asyncio.run(main())
```

### gRPC API
- **Put**: Stores a key-value pair.
- **Get**: Retrieves a value for a given key.
- **Delete**: Removes a key-value pair.
- **ListKeys**: Returns all stored keys.
- **Backup**: Creates a database backup.

## Testing
Run correctness, failure recovery, and performance tests:
```sh
PYTHONPATH=$(pwd) pytest -v tests/
```

## Documentation
- **[API Reference](/docs/api_reference.md)**: `docs/api_reference.md`    

- **[Design Decisions](/docs/design_decisions.md)**: `docs/design_decisions.md`    
- **[Project Report](/docs/Project_report.md)**: `docs/Project_report.md`    


---

### **Client CLI Usage Instructions**

### **Interactive Mode (`client_cli.py`)**
The interactive CLI allows users to send **Put** and **Get** requests to the distributed key-value store via terminal input.

### **Running the Interactive CLI**
Run the script directly:
```bash
python client_cli.py
```

### **Available Commands**
- `put <key> <value>` – Stores a key-value pair.
- `get <key>` – Retrieves the value of a key.
- `exit` – Quits the CLI.

### **Example Usage**
```bash
kvstore> put foo bar
Old Value: None

kvstore> get foo
Value: bar

kvstore> get unknown_key
Value: Key not found

kvstore> exit
Exiting...
```

---

### **Batch Mode (`client_batch.py`)**
The batch CLI reads **multiple** `put` and `get` commands from a text file and executes them sequentially.

### **Running the Batch CLI**
```bash
python client_batch.py /path/to/commands.txt
```
Where `/path/to/commands.txt` is a file containing the list of key-value operations.

### **Example `commands.txt`**
```
put key1 value1
put key2 value2
get key1
get unknown_key
```

### **Expected Output**
```
Batch Execution Results:
PUT key1 -> Old Value: None
PUT key2 -> Old Value: None
GET key1 -> Value: value1
GET unknown_key -> Value: Key not found
```

### **Error Handling**
- If the file does not exist:  
  ```
  Error: File not found: commands.txt
  ```
- If an invalid command is present:  
  ```
  Invalid command: delete key1
  ```

These CLI tools make it easy to interact with the key-value store both **manually** and through **batch processing**. 

---



