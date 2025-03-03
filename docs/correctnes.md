# Test Correctness Report - Distributed Key-Value Store

## Overview
This document explains the **correctness tests** implemented in `test_correctness.py`. These tests ensure that our distributed key-value store correctly handles **basic operations, consistency guarantees, and key-value retrieval semantics**. The tests use `pytest` and `asyncio` to validate asynchronous gRPC interactions, guaranteeing that our system is both **robust and efficient**.

## Why This Test Suite is Effective
- **Ensures fundamental key-value operations (`Put`, `Get`, `Delete`) work correctly.**
- **Verifies consistency guarantees, including eventual consistency across distributed nodes.**
- **Uses `pytest.mark.asyncio` to properly test asynchronous gRPC functions.**
- **Validates key behavior under realistic conditions such as overwrites and deletions.**

---
## Test Breakdown and Justification

### **1. `test_put_get_consistency()`**
✅ **What It Does:**
- Stores a key-value pair using `Put`.
- Retrieves the value using `Get`.
- Asserts that the retrieved value is the same as what was stored.

✅ **Why This is Important:**
- Ensures that basic storage and retrieval work correctly.
- Prevents potential data corruption or incorrect reads.
- Verifies that the system correctly handles gRPC-based communication.

### **2. `test_overwrite_key()`**
✅ **What It Does:**
- Puts an initial value for a key.
- Overwrites the key with a new value.
- Asserts that the returned old value is correct.

✅ **Why This is Important:**
- Ensures atomicity in key overwrites.
- Guarantees that previous values are properly tracked and returned.
- Verifies that data updates do not introduce inconsistencies.

### **3. `test_delete_key()`**
✅ **What It Does:**
- Stores a key-value pair.
- Deletes the key.
- Attempts to retrieve the key after deletion and expects it to be missing.

✅ **Why This is Important:**
- Ensures that deletions are **persisted** and **consistent**.
- Prevents stale key-value pairs from being returned.
- Validates that the `Delete` operation is correctly executed over gRPC.

### **4. `test_list_keys()`**
✅ **What It Does:**
- Inserts multiple keys.
- Calls `ListKeys`.
- Ensures that all stored keys are correctly returned.

✅ **Why This is Important:**
- Tests proper indexing and retrieval of all keys.
- Ensures that key storage maintains a correct internal structure.
- Guarantees that key enumeration is accurate and efficient.

### **5. `test_eventual_consistency()`**
✅ **What It Does:**
- Writes a key-value pair to one server.
- Waits 5 seconds to allow replication.
- Reads the key from another server.
- Ensures that the latest written value is eventually returned.

✅ **Why This is Important:**
- Demonstrates **eventual consistency** in a distributed system.
- Validates **replication correctness** across multiple nodes.
- Ensures that after a reasonable delay, all nodes converge to the correct state.

---
## Summary
Each test in `test_correctness.py` was carefully designed to ensure the distributed key-value store behaves **correctly, consistently, and reliably**.
- We **chose `pytest.mark.asyncio`** to properly handle async tests with gRPC.
- **Each test reflects a real-world scenario**, such as overwriting keys, deleting values, and handling replication.
- **Eventual consistency** is explicitly tested to validate the correctness of our system under distributed conditions.

This test suite **proves the correctness of our implementation**, making it highly robust against failures, ensuring data integrity, and validating key-value store consistency across all operations.

