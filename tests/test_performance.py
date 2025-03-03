import pytest
import asyncio
import time
import sys
import os
# Ensure the server module is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../server")))
import client
from client.kv_client import KeyValueClient
import random
import numpy as np
import subprocess
import pytest
import asyncio
import time


@pytest.mark.asyncio
async def test_throughput():
    """Test how many requests per second the system can handle for both PUT and GET."""

    client = KeyValueClient(["localhost:50051"])
    await client.initialize()
    num_requests = 1000

    # Measure throughput for PUT requests
    start_time = time.time()
    put_tasks = [client.put(f"key{i}", f"value{i}") for i in range(num_requests)]
    try:
        await asyncio.gather(*put_tasks)
    except Exception as e:
        pytest.fail(f"An error occurred during PUT requests: {str(e)}")
    put_end_time = time.time()
    put_throughput = num_requests / (put_end_time - start_time)
    print(f"PUT Throughput: {put_throughput:.2f} requests/sec")

    # Measure throughput for GET requests
    start_time = time.time()
    get_tasks = [client.get(f"key{i}") for i in range(num_requests)]
    try:
        await asyncio.gather(*get_tasks)
    except Exception as e:
        pytest.fail(f"An error occurred during GET requests: {str(e)}")
    get_end_time = time.time()
    get_throughput = num_requests / (get_end_time - start_time)
    print(f"GET Throughput: {get_throughput:.2f} requests/sec")

    assert put_throughput > 100, "PUT throughput is too low"
    assert get_throughput > 100, "GET throughput is too low"


@pytest.mark.asyncio
async def test_latency():
    """Measure request latency for both PUT and GET requests."""

    client = KeyValueClient(["localhost:50051"])
    await client.initialize()
    num_requests = 100

    put_latencies = []
    get_latencies = []

    # Measure latency for PUT requests
    for i in range(num_requests):
        try:
            start_time = time.time()
            result = await client.put(f"latency_test_{i}", "test_value")
            if result == "":
                raise ValueError(f"PUT operation failed for key 'latency_test_{i}'")
            end_time = time.time()
            put_latencies.append((end_time - start_time) * 1000)
        except Exception as e:
            print(f"Error with PUT request {i}: {e}")
            put_latencies.append(None)
    
    # Measure latency for GET requests
    for i in range(num_requests):
        try:
            start_time = time.time()
            result = await client.get(f"latency_test_{i}")
            if result is None:
                raise ValueError(f"GET operation failed for key 'latency_test_{i}'")
            end_time = time.time()
            get_latencies.append((end_time - start_time) * 1000)
        except Exception as e:
            print(f"Error with GET request {i}: {e}")
            get_latencies.append(None)

    # Remove failed requests
    put_latencies = [lat for lat in put_latencies if lat is not None]
    get_latencies = [lat for lat in get_latencies if lat is not None]

    if put_latencies:
        avg_put_latency = sum(put_latencies) / len(put_latencies)
        print(f"Average PUT Latency: {avg_put_latency:.2f} ms")
        assert avg_put_latency < 100, f"Average PUT latency is too high: {avg_put_latency:.2f} ms"
    else:
        print("All PUT requests failed. Cannot calculate average latency.")

    if get_latencies:
        avg_get_latency = sum(get_latencies) / len(get_latencies)
        print(f"Average GET Latency: {avg_get_latency:.2f} ms")
        assert avg_get_latency < 200, f"Average GET latency is too high: {avg_get_latency:.2f} ms"
    else:
        print("All GET requests failed. Cannot calculate average latency.")



@pytest.mark.asyncio
async def test_hot_cold_distribution():
    """Test performance with hot/cold key distribution (10% keys receive 90% of requests)."""
    
    client = KeyValueClient(["localhost:50051"])
    await client.initialize()
    num_requests = 1000
    hot_keys = [f"hot_key{i}" for i in range(10)]
    cold_keys = [f"cold_key{i}" for i in range(90)]

    # Preload hot keys with initial values
    await asyncio.gather(*[client.put(key, "initial_value") for key in hot_keys])

    start_time = time.time()
    
    write_latencies = []
    read_latencies = []

    async def write_load():
        tasks = []
        for i in range(num_requests):
            key = hot_keys[i % len(hot_keys)] if i < 900 else cold_keys[i % len(cold_keys)]
            write_start = time.time()
            tasks.append(client.put(key, f"value_{i}"))
            write_latencies.append((time.time() - write_start) * 1000)  # Convert to ms
        await asyncio.gather(*tasks)

    async def read_load():
        for _ in range(500):  # 500 GET requests on hot keys
            key = random.choice(hot_keys)
            read_start = time.time()
            await client.get(key)
            read_latencies.append((time.time() - read_start) * 1000)  # Convert to ms

    await asyncio.gather(write_load(), read_load())  # Run both tasks concurrently

    end_time = time.time()
    throughput = num_requests / (end_time - start_time)

    # Compute average latencies
    avg_write_latency = sum(write_latencies) / len(write_latencies)
    avg_read_latency = sum(read_latencies) / len(read_latencies)

    print(f"Throughput with Hot/Cold Distribution: {throughput:.2f} requests/sec")
    print(f"Average Write Latency: {avg_write_latency:.4f} ms")
    print(f"Average Read Latency: {avg_read_latency:.2f} ms")

    # Assertions for performance constraints (Adjust thresholds as needed)
    assert throughput > 50, f"Throughput too low: {throughput:.2f} req/sec"
    assert avg_write_latency < 100, f"Write latency too high: {avg_write_latency:.2f} ms"
    assert avg_read_latency < 100, f"Read latency too high: {avg_read_latency:.2f} ms"


@pytest.mark.asyncio
async def test_mixed_read_write():
    """Test throughput and latency for a mixed 70% GET and 30% PUT workload with Zipfian key access."""
    
    client = KeyValueClient(["localhost:50051"])
    await client.initialize()
    num_requests = 1000  # Total operations
    num_keys = 100  # Total distinct keys
    put_probability = 0.3  # Probability of a PUT request

    keys = [f"key{i}" for i in range(num_keys)]  # Generate 100 unique keys

    # Pre-load all keys with initial values
    await asyncio.gather(*[client.put(key, "initial_value") for key in keys])

    # Generate a Zipfian distribution of keys (skewed access)
    zipf_keys = np.random.zipf(1.2, num_requests) % num_keys  # Generates indexes for key access
    key_access_pattern = [keys[i] for i in zipf_keys]  # Map indexes to actual keys

    semaphore = asyncio.Semaphore(100)  # Limit concurrency to avoid system overload

    async def limited_task(task):
        async with semaphore:
            await asyncio.sleep(random.uniform(0.001, 0.005))
            start_time = time.time()
            result = await task
            return time.time() - start_time, result  # Return latency and response

    start_time = time.time()

    tasks = []
    for i in range(num_requests):
        key = key_access_pattern[i]  # Select key based on Zipfian distribution
        if random.random() < put_probability:
            task = client.put(key, f"value_{i}")
        else:
            task = client.get(key)
        tasks.append(limited_task(task))  # Store latency measurement

    # Collect results first to prevent coroutine warnings
    resolved_results = await asyncio.gather(*tasks)

    end_time = time.time()

    # Process latencies from resolved results
    get_latencies = [lat for lat, res in resolved_results if res is not None and isinstance(res, str)]  # GET responses
    put_latencies = [lat for lat, res in resolved_results if res is not None and not isinstance(res, str)]  # PUT responses

    avg_get_latency = (sum(get_latencies) / len(get_latencies)) * 1000 if get_latencies else 0
    avg_put_latency = (sum(put_latencies) / len(put_latencies)) * 1000 if put_latencies else 0

    throughput = num_requests / (end_time - start_time)

    print(f"Mixed Workload Throughput: {throughput:.2f} requests/sec")
    print(f"Average GET Latency: {avg_get_latency:.2f} ms")
    print(f"Average PUT Latency: {avg_put_latency:.2f} ms")

    # Assertions for performance
    assert throughput > 50, f"Throughput too low: {throughput:.2f} req/sec"
    assert avg_get_latency < 300, f"GET latency too high: {avg_get_latency:.2f} ms"
    assert avg_put_latency < 200, f"PUT latency too high: {avg_put_latency:.4f} ms"


@pytest.mark.asyncio
async def test_high_concurrency():
    """Test system performance under high concurrent load."""
    client = KeyValueClient()
    num_clients = 100  # Simulate 100 concurrent clients
    num_requests_per_client = 50
    total_requests = num_clients * num_requests_per_client
    semaphore = asyncio.Semaphore(50)  # Limit concurrency

    latencies = []

    async def client_task(client_id):
        for i in range(num_requests_per_client):
            key = f"client_{client_id}_key{i}"
            value = f"value_{i}"
            async with semaphore:  # Limit concurrent requests
                start = time.time()
                await client.put(key, value)
                latencies.append(time.time() - start)

    start_time = time.time()

    await asyncio.gather(*[client_task(i) for i in range(num_clients)])

    end_time = time.time()
    throughput = total_requests / (end_time - start_time)
    avg_latency = (sum(latencies) / len(latencies)) * 1000  # Convert to ms

    print(f"Throughput with High Concurrency: {throughput:.2f} requests/sec")
    print(f"Average Request Latency: {avg_latency:.2f} ms")

    # Assertions for performance
    assert throughput > 300, f"Throughput too low: {throughput:.2f} req/sec"
    assert avg_latency < 200, f"Latency too high: {avg_latency:.2f} ms"

@pytest.mark.asyncio
async def test_performance_under_failure():
    """Measure system throughput when one node is temporarily unavailable."""
    client1 = KeyValueClient(["localhost:50051"])
    client2 = KeyValueClient(["localhost:50052"])

    await client1.initialize()
    await client2.initialize()

    num_requests = 1000

    # Simulate node failure asynchronously
    print("Stopping server on port 50052...")
    process = await asyncio.create_subprocess_exec("pkill", "-f", "python server/async_server.py --port=50052")
    await process.wait()
    await asyncio.sleep(2)  # Allow system to register failure

    start_time = time.time()
    successful_requests = 0

    async def put_with_retries(key, value, retries=3):
        """Try PUT request with limited retries."""
        for attempt in range(retries):
            try:
                await client1.put(key, value)
                return True
            except Exception as e:
                print(f"Retry {attempt+1}/{retries} for key {key} failed: {e}")
                await asyncio.sleep(0.5)  # Wait before retrying
        return False

    # Perform PUT requests with retry logic
    tasks = [put_with_retries(f"failure_test_{i}", f"value_{i}") for i in range(num_requests)]
    results = await asyncio.gather(*tasks)
    successful_requests = sum(results)

    end_time = time.time()
    throughput = successful_requests / (end_time - start_time)
    print(f"Throughput under node failure: {throughput:.2f} requests/sec")

    # Restart server asynchronously
    print("Restarting server on port 50052...")
    await asyncio.create_subprocess_exec("python", "server/async_server.py", "--port=50052", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(10)  # Give time for server to restart

    # Assertions
    assert successful_requests > 0, "All PUT operations failed under node failure!"
    assert throughput > 20, f"Throughput too low: {throughput:.2f} req/sec"
