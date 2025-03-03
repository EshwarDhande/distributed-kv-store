# Test Report - Distributed Key-Value Store

## Overview
This document consolidates the **correctness, failure recovery, and performance** testing of our distributed key-value store. These tests ensure that the system functions correctly, handles failures gracefully, and performs efficiently under various workloads.

---
## 1. Correctness Testing

### **Test 1: `test_put_get_consistency()`**
- **Purpose:**  
  Ensures that storing and retrieving key-value pairs work as expected.
- **Significance:**  
  Prevents incorrect reads, ensuring data integrity.

### **Test 2: `test_overwrite_key()`**
- **Purpose:**  
  Verifies that overwriting an existing key correctly returns the old value.
- **Significance:**  
  Ensures atomic updates and prevents stale data issues.

### **Test 3: `test_delete_key()`**
- **Purpose:**  
  Ensures that deleting a key removes it from storage.
- **Significance:**  
  Prevents unexpected stale reads after deletions.

### **Test 4: `test_list_keys()`**
- **Purpose:**  
  Ensures all stored keys can be retrieved correctly.
- **Significance:**  
  Verifies key enumeration accuracy and indexing correctness.

### **Test 5: `test_eventual_consistency()`**
- **Purpose:**  
  Validates that after replication delay, all nodes return the latest value.
- **Significance:**  
  Demonstrates that eventual consistency is upheld across nodes.

---
## 2. Failure Recovery Testing

### **Test 6: `test_recovery_from_failure()`**
- **Purpose:**  
  Ensures data remains intact after server crashes and restarts.
- **Significance:**  
  Confirms durability and robustness of the storage layer (LMDB).

### **Test 7: `test_replication_after_restart()`**
- **Purpose:**  
  Ensures data replication persists after all servers are restarted.
- **Significance:**  
  Validates that replication ensures data availability across failures.

### **Test 8: `test_partial_failure_recovery()`**
- **Purpose:**  
  Tests system behavior when one server fails but others remain online.
- **Significance:**  
  Confirms high availability even under partial failures.

### **Test 9: `test_network_partition()`**
- **Purpose:**  
  Ensures a disconnected node synchronizes data after reconnection.
- **Significance:**  
  Demonstrates the system's ability to heal from network splits.

### **Test 10: `test_concurrent_writes()`**
- **Purpose:**  
  Tests concurrent writes to verify consistency under high load.
- **Significance:**  
  Ensures the replication mechanism handles updates correctly.

---
## 3. Performance Testing

### **Test 11: `test_throughput()`**
- **Purpose:**  
  Measures the number of requests per second the system can handle.
- **Significance:**  
  Evaluates the efficiency of request processing.

### **Test 12: `test_latency()`**
- **Purpose:**  
  Measures individual request latencies for key-value operations.
- **Significance:**  
  Ensures response times meet performance expectations.

### **Test 13: `test_hot_cold_distribution()`**
- **Purpose:**  
  Simulates real-world workloads where some keys are accessed more frequently than others.
- **Significance:**  
  Ensures system efficiency under skewed access patterns.

### **Test 14: `test_mixed_read_write()`**
- **Purpose:**  
  Evaluates system performance under a 70% GET / 30% PUT workload.
- **Significance:**  
  Ensures read-heavy workloads are handled efficiently.

### **Test 15: `test_high_concurrency()`**
- **Purpose:**  
  Simulates 100+ concurrent clients to measure scalability.
- **Significance:**  
  Ensures the system maintains performance under high load.

### **Test 16: `test_performance_under_failure()`**
- **Purpose:**  
  Measures performance when one server fails during high-load operations.
- **Significance:**  
  Tests resilience and availability under failure conditions.

---
## Summary
- **Correctness tests confirm** that key-value operations work as expected, ensuring consistency and correctness.
- **Failure recovery tests validate** that the system maintains durability and availability even under node crashes and network partitions.
- **Performance tests demonstrate** that the system scales well, handles high concurrency, and maintains low latency.

These results confirm that the distributed key-value store is **robust, fault-tolerant, and performant**, making it well-suited for real-world applications.

