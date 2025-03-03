import pytest
import asyncio
import subprocess
import time
import sys
import os

# Ensure the server module is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../server")))
import client
from client.kv_client import KeyValueClient

@pytest.mark.asyncio
async def test_recovery_from_failure():
    """Test if system recovers from server failure."""

    client = KeyValueClient(["localhost:50051"])
    await client.initialize()

    await client.put("crash_test", "before_crash")
    
    # Simulate server crash
    subprocess.run(["pkill", "-f", "async_server.py"])  # Kill all servers
    time.sleep(2)  # Allow time for shutdown
    
    # Restart servers
    subprocess.run(["bash", "scripts/start_servers.sh"])
    time.sleep(2)  # Allow time for restart
    
    # Ensure key still exists
    value = await client.get("crash_test")
    
    assert value == "before_crash", f"Expected 'before_crash', got '{value}'"



@pytest.mark.asyncio
async def test_replication_after_restart():
    """Test if replicated data is available after a node restart."""
    
    client = KeyValueClient(["localhost:50051"])
    await client.initialize()  # Ensure initialization

    # Store a key
    await client.put("replica_key", "replicated_value")

    # Kill all servers
    subprocess.run(["pkill", "-f", "async_server.py"])
    time.sleep(2)  # Ensure processes exit

    # Restart all nodes
    processes = [
        subprocess.Popen(["python", "server/async_server.py", "--port=50051"]),
        subprocess.Popen(["python", "server/async_server.py", "--port=50052"]),
        subprocess.Popen(["python", "server/async_server.py", "--port=50053"]),
    ]
    time.sleep(5)  # Allow servers to start fully

    # Create a new client after restart
    client_after_restart = KeyValueClient(["localhost:50051"])
    await client_after_restart.initialize()

    # Wait for server to become ready
    async def wait_for_server_ready(client, key, expected_value, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            value = await client.get(key)
            if value == expected_value:
                return True
            await asyncio.sleep(1)  # Retry after 1 sec
        return False

    assert await wait_for_server_ready(client_after_restart, "replica_key", "replicated_value"), "Replication failed after restart"


@pytest.mark.asyncio
async def test_partial_failure_recovery():
    """Test if data remains available when one server fails."""

    client1 = KeyValueClient(["localhost:50051"])
    client2 = KeyValueClient(["localhost:50052"])

    await client1.initialize()
    await client2.initialize()

    await client1.put("partial_fail_key", "survives")

    # Kill one node
    subprocess.run(["pkill", "-f", "async_server.py", "--port=50052"])
    time.sleep(2)

    # Ensure data is still available from the other node
    value = await client1.get("partial_fail_key")
    assert value == "survives", f"Expected 'survives', got '{value}'"

    # Restart failed node
    subprocess.Popen(["python", "server/async_server.py", "--port=50052"])
    time.sleep(5)

    value = await client2.get("partial_fail_key")
    assert value == "survives", f"Expected 'survives' after recovery, got '{value}'"



@pytest.mark.asyncio
async def test_network_partition():
    """Test if a temporarily disconnected node catches up after reconnection."""
    client1 = KeyValueClient(["localhost:50051"])
    client2 = KeyValueClient(["localhost:50052"])

    await client1.initialize()
    await client2.initialize()

    await client1.put("partition_key", "before_partition")

    # Simulate network partition (stop one server temporarily)
    print("Stopping server on port 50052...")
    subprocess.run(["pkill", "-f", "python server/async_server.py --port=50052"])  # Ensures exact match
    time.sleep(2)  # Wait for process shutdown

    # Update value while node is down
    await client1.put("partition_key", "after_partition")

    # Restart partitioned node in the background
    print("Restarting server on port 50052...")
    subprocess.Popen(["python", "server/async_server.py", "--port=50052"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Wait for the server to become available
    async def wait_for_server(host, port, timeout=15):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                reader, writer = await asyncio.open_connection(host, port)
                writer.close()
                await writer.wait_closed()
                return True  # Server is up
            except (ConnectionRefusedError, OSError):
                await asyncio.sleep(1)
        return False

    if not await wait_for_server("localhost", 50052):
        pytest.fail("Server did not restart in time")

    # Wait for server to sync up
    async def wait_for_catchup(client, key, expected_value, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            value = await client.get(key)
            if value == expected_value:
                return True
            await asyncio.sleep(1)
        return False

    assert await wait_for_catchup(client2, "partition_key", "after_partition"), "Partitioned node did not catch up!"



@pytest.mark.asyncio
async def test_concurrent_writes():
    """Test if concurrent writes and reads ensure eventual consistency."""
    
    client1 = KeyValueClient(["localhost:50051"])
    client2 = KeyValueClient(["localhost:50052"])

    await client1.initialize()
    await client2.initialize()

    observed_values = []

    async def writer():
        """Writes a new value every second."""
        for i in range(5):
            await client1.put("concurrent_key", f"value_{i}")
            await asyncio.sleep(1)

    async def reader():
        """Reads the key every second, tracking all observed values."""
        timeout = 15  # Allow 15 seconds for eventual consistency
        start_time = time.time()

        while time.time() - start_time < timeout:
            value = await client2.get("concurrent_key")
            if value is not None:
                observed_values.append(value)
                if value == "value_4":
                    return  # Stop once we confirm the latest value
            await asyncio.sleep(1)

        pytest.fail(f"Replication failed: observed values {observed_values}")

    await asyncio.gather(writer(), reader())

    assert "value_4" in observed_values, f"Final expected value 'value_4' not seen. Observed: {observed_values}"


