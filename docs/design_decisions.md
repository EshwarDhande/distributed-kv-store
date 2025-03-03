# Design Decisions - Distributed Key-Value Store

## 1. **Architecture Choice: Shared-Nothing Design**
- Each server instance operates independently without shared memory or file access.
- Communication between instances occurs via explicit gRPC-based messaging.
- This improves fault isolation, scalability, and resilience to failures.

## 2. **Asynchronous Server Implementation**
- Implemented using `async_server.py`, leveraging `asyncio` and gRPC for non-blocking I/O.
- Allows high concurrency while handling multiple client requests efficiently.
- Reduces thread contention and improves throughput compared to synchronous models.

## 3. **Storage Backend: LMDB**
- Chosen for its **low-latency, high-throughput** key-value storage.
- Supports **ACID transactions**, ensuring data integrity.
- Implements **copy-on-write** for efficient snapshot backups.
- Managed via `lmdb_store.py`, handling read/write operations and backups.

## 4. **Client Library (`kv_client.py`)**
- Provides an asynchronous gRPC client for communication with the server.
- Implements `Put`, `Get`, `Delete`, and `ListKeys` functions.
- Handles connection initialization (`kv_init`) and shutdown (`kv_shutdown`).
- Ensures non-blocking operations for optimal performance.

## 5. **Replication Strategy**
- Implemented in `replication.py` using **gRPC-based replication**.
- Each server maintains copies of key-value pairs on peer nodes.
- Ensures eventual consistency by retrying failed replication attempts.
- Handles network partitions and ensures updates propagate after recovery.

## 6. **Failure Handling & Recovery**
- Supports process halting failures but not OS or machine crashes.
- Upon restart, servers restore state from persistent LMDB storage.
- **Backup & Restore**:
  - Manual and automatic backup support via the `Backup` gRPC API.
  - `lmdb_store.py` copies the database to `lmdb_backup/` for durability.

## 7. **Consistency Model: Eventual Consistency**
- Clients may read stale data during network partitions.
- Replication ensures all nodes eventually converge to the latest state.
- Strong consistency was avoided to prioritize availability and performance.

## 8. **Performance Optimizations**
- **Multiprocessing Worker (`multiproc_worker.py`)**: Uses worker threads for parallel DB operations.
- **Batched Replication**: Reduces network overhead by grouping updates.
- **Non-blocking Client Requests**: Uses async I/O to avoid blocking operations.

## 9. **Security Considerations**
- gRPC over insecure channels (can be extended to use TLS).
- Input validation to enforce key and value constraints.


