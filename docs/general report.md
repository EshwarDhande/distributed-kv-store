# Distributed Key-Value Store - Project Report

## 1. Introduction
This report presents the implementation of a **distributed key-value store** using a **shared-nothing architecture** with **gRPC-based communication**. The system ensures **eventual consistency**, fault tolerance, and optimized performance for various workload distributions.

## 2. Implementation Details

### 2.1 Client Implementation (`kv_client.py`)
- Provides an **asynchronous gRPC client** for server communication.
- Supports `Put`, `Get`, `Delete`, `ListKeys`, and `Backup` operations.
- Handles **server initialization (`kv_init`) and shutdown (`kv_shutdown`)**.
- Uses **non-blocking operations** for efficiency.

### 2.2 Server Implementation (`async_server.py`)
- Implements an **asynchronous gRPC server** using `asyncio`.
- Handles **multiple concurrent client requests efficiently**.
- Manages **persistent storage** using LMDB (`lmdb_store.py`).

### 2.3 Storage Backend (LMDB)
- **Lightweight and efficient key-value storage**.
- **ACID transactions** ensure data integrity.
- **Copy-on-write** support for safe backups.
- Backup functionality managed by `lmdb_store.py`.

### 2.4 Replication Mechanism (`replication.py`)
- **Ensures data availability across nodes** using gRPC-based replication.
- **Retries failed replication attempts** to maintain consistency.
- **Handles network partitions** and ensures updates propagate after recovery.

### 2.5 Failure Handling & Recovery
- Supports **process halting failures** but not OS/machine crashes.
- Recovers state from **persistent LMDB storage upon restart**.
- **Backup API** allows explicit database snapshots for recovery.

## 3. Protocol Specification
The system uses a **gRPC-based API** defined in `kvstore.proto`. The key methods include:
- **Put(KeyValue) -> OldValue**: Stores a key-value pair.
- **Get(Key) -> Value**: Retrieves a value for a given key.
- **Delete(Key) -> Empty**: Deletes a key-value pair.
- **ListKeys(Empty) -> KeyList**: Returns all stored keys.
- **Backup(Empty) -> BackupStatus**: Creates a database backup.

## 4. Testing & Evaluation

### 4.1 Correctness Testing (`test_correctness.py`)
- Verifies key-value operations (`Put`, `Get`, `Delete`).
- Ensures **eventual consistency** after network partitions.
- Tests replication correctness across multiple nodes.

### 4.2 Failure Recovery Testing (`test_failures.py`)
- Simulates **server crashes and restarts**.
- Ensures stored data persists across failures.
- Tests **replication after node failures**.

### 4.3 Performance Testing (`test_performance.py`)
- **Throughput Testing**: Measures requests per second under load.
- **Latency Testing**: Evaluates response times for different workloads.
- **Hot/Cold Key Distribution**: Tests system behavior under skewed access patterns.
- **High Concurrency Load**: Simulates 100+ clients performing simultaneous operations.

## 5. Results & Analysis
- **Correctness**: All tests pass, ensuring expected key-value store behavior.
- **Failure Recovery**: Data remains available after process restarts.
- **Performance**:
  - Achieves **high throughput (~1000+ requests/sec in benchmarks)**.
  - **Low latency (<50ms average for GET operations)**.
  - **Handles concurrent writes efficiently** with worker-based processing.

## 6. Conclusion
This project successfully implements a distributed key-value store with **efficient storage, replication, and failure recovery mechanisms**. Future work could explore **stronger consistency models, leader-based coordination, and enhanced security measures**.

