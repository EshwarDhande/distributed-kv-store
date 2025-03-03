# Test Failures Report - Distributed Key-Value Store

## Overview
This document explains the **failure handling tests** implemented in `test_failures.py`. These tests ensure that our distributed key-value store correctly recovers from failures, maintains data consistency, and preserves replication guarantees.

## Why This Test Suite is Effective
- **Validates server recovery from crashes and restarts.**
- **Ensures data persistence across failures.**
- **Tests eventual consistency by simulating network partitions.**
- **Verifies replication integrity after failure and recovery.**

---
## Test Breakdown and Justification

### **1. `test_recovery_from_failure()`**
✅ **What It Does:**
- Stores a key-value pair.
- Simulates a server crash using `pkill`.
- Restarts the server and verifies that the data is still available.

✅ **Why This is Important:**
- Ensures data persistence across process failures.
- Tests LMDB's durability in preserving data after unexpected shutdowns.
- Confirms that restarting the server does not result in data loss.

### **2. `test_replication_after_restart()`**
✅ **What It Does:**
- Stores a key-value pair before shutting down all servers.
- Restarts all nodes and verifies if the key-value pair is still accessible.
- Implements a **wait-for-server-ready mechanism** to handle race conditions.

✅ **Why This is Important:**
- Ensures that replicated data remains available after node restarts.
- Validates the effectiveness of replication in preserving system state.
- Tests gRPC's ability to handle reconnections and data recovery.

### **3. `test_partial_failure_recovery()`**
✅ **What It Does:**
- Stores a key-value pair while multiple servers are running.
- Kills one server and ensures the remaining node can still serve the data.
- Restarts the failed server and verifies that data is still accessible.

✅ **Why This is Important:**
- Simulates **real-world distributed system failures**.
- Ensures **high availability** even when a node goes down.
- Confirms that restarted nodes sync correctly with active nodes.

### **4. `test_network_partition()`**
✅ **What It Does:**
- Writes a key-value pair to one server.
- Simulates a **network partition** by stopping a second server.
- Writes a new value while the second node is offline.
- Restarts the partitioned node and ensures it **catches up** with the latest value.

✅ **Why This is Important:**
- Verifies **eventual consistency** in a distributed system.
- Ensures that updates applied during a partition are propagated after reconnection.
- Tests the ability of the system to **heal from network splits**.

### **5. `test_concurrent_writes()`**
✅ **What It Does:**
- Runs a **writer process** that continuously updates a key.
- Simultaneously runs a **reader process** that tracks observed values.
- Asserts that the final value matches the last written update.

✅ **Why This is Important:**
- Ensures that concurrent writes do not cause inconsistency.
- Tests **replication correctness under concurrent load**.
- Verifies that eventual consistency is upheld even with rapid updates.

---
## Summary
Each test in `test_failures.py` was designed to ensure **fault tolerance, data durability, and high availability**.
- **We simulate real-world failures**, including crashes, network partitions, and node failures.
- **Replication and recovery mechanisms are validated** to ensure data remains accessible.
- **Concurrency is tested** to confirm that replication handles real-time updates efficiently.

These tests demonstrate that our system can **withstand failures, recover effectively, and maintain eventual consistency**, making it highly resilient in distributed environments.

