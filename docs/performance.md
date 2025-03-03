# Test Performance Report - Distributed Key-Value Store

## Overview
This document details the **performance testing** implemented in `test_performance.py`. These tests evaluate the system’s **throughput, latency, and resilience under high concurrency and failures**.

## Why This Test Suite is Effective
- **Measures system throughput under normal and stressed conditions.**
- **Evaluates request latency across different workloads.**
- **Simulates real-world access patterns, including hot/cold distributions and Zipfian workloads.**
- **Tests performance degradation and recovery when nodes fail.**

---
## Test Breakdown and Justification

### **1. `test_throughput()`**
✅ **What It Does:**
- Sends **1000 concurrent `Put` requests** to measure how many requests per second the system can handle.
- Uses `asyncio.gather()` for parallel execution.
- Calculates total throughput.

✅ **Why This is Important:**
- Measures the **maximum sustained request rate**.
- Identifies potential bottlenecks in the system.
- Ensures efficient handling of bulk write operations.

### **2. `test_latency()`**
✅ **What It Does:**
- Measures **individual request latency** for `Put` operations.
- Stores latencies for each request and calculates an **average latency**.
- Ensures **error handling** in case of failures.

✅ **Why This is Important:**
- Provides insights into **response times under load**.
- Helps optimize **network and database access performance**.
- Ensures system meets **low-latency requirements** for real-world applications.

### **3. `test_hot_cold_distribution()`**
✅ **What It Does:**
- Implements a **hot/cold key access pattern**:
  - **90% of requests go to 10% of keys (hot keys).**
  - **Remaining 10% of requests go to 90% of keys (cold keys).**
- Measures throughput and latency for both read and write operations.

✅ **Why This is Important:**
- Simulates **real-world workload distributions** seen in caching and database systems.
- Ensures system handles **skewed access patterns efficiently**.
- Evaluates **write amplification effects** and database performance.

### **4. `test_mixed_read_write()`**
✅ **What It Does:**
- Implements a **70% GET / 30% PUT mixed workload**.
- Uses a **Zipfian distribution** to skew access patterns.
- Measures **latency and throughput for both read and write operations**.

✅ **Why This is Important:**
- Simulates common workloads in real-world key-value stores (e.g., caching layers).
- Tests how well the system balances **read-heavy vs. write-heavy operations**.
- Ensures that even under load, **reads remain efficient**.

### **5. `test_high_concurrency()`**
✅ **What It Does:**
- Simulates **100 concurrent clients**, each sending **50 requests**.
- Uses `asyncio.Semaphore` to **control request bursts**.
- Measures **total throughput and request latency** under high concurrency.

✅ **Why This is Important:**
- Evaluates **how the system scales under concurrent workloads**.
- Ensures the system can handle **high client concurrency without performance degradation**.
- Tests synchronization mechanisms and request queue efficiency.

### **6. `test_performance_under_failure()`**
✅ **What It Does:**
- Simulates a **node failure** by shutting down one server during a high-load test.
- Measures how well the system maintains throughput despite a failure.
- Restarts the failed node and verifies if throughput recovers.

✅ **Why This is Important:**
- Ensures **system resilience under failure conditions**.
- Validates **data availability guarantees** when nodes temporarily go offline.
- Demonstrates that the system maintains acceptable performance even when degraded.

---
## Summary
Each test in `test_performance.py` was designed to ensure the **distributed key-value store operates efficiently under high load and failure conditions**.
- **Throughput and latency benchmarks validate system performance.**
- **Skewed workload distributions simulate real-world database usage.**
- **Failure simulation confirms the system remains operational under disruptions.**

These tests demonstrate that our system achieves **high performance, low latency, and resilience to failures**, making it robust for production-level distributed environments.