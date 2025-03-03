import pytest
import asyncio
import sys
import os

# Ensure the server module is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../server")))
import client
from client.kv_client import KeyValueClient

@pytest.mark.asyncio
async def test_put_get_consistency():
    """Test if PUT and GET return consistent results."""

    client = KeyValueClient(["localhost:50051"])
    await client.initialize()  # Ensure initialization
    
    await client.put("test_key", "test_value")   
    value = await client.get("test_key")
    
    assert value == "test_value", f"Expected 'test_value', got '{value}'"


@pytest.mark.asyncio
async def test_overwrite_key():
    """Test if overwriting a key returns the correct old value."""

    client = KeyValueClient(["localhost:50051"])
    await client.initialize()
    
    await client.put("overwrite_key", "first_value")
    
    # Overwrite with a new value
    old_value = await client.put("overwrite_key", "new_value")
    
    assert old_value == "first_value", f"Expected 'first_value', got '{old_value}'"


@pytest.mark.asyncio
async def test_delete_key():
    """Test if DELETE removes a key and GET fails afterward."""

    client = KeyValueClient(["localhost:50051"])
    await client.initialize()
   
    # Store and delete key
    await client.put("delete_key", "delete_value")
    await client.delete("delete_key")   
    # Try to GET the deleted key
    value = await client.get("delete_key")
    
    assert value is "", f"Expected None, got '{value}'"

@pytest.mark.asyncio
async def test_list_keys():
    """Test if LIST returns all stored keys."""

    client = KeyValueClient(["localhost:50051"])
    await client.initialize()
   
    # Insert multiple keys
    await client.put("key1", "val1")
    await client.put("key2", "val2")    
    keys = await client.list_keys()
    
    assert "key1" in keys and "key2" in keys, f"Keys not found: {keys}"

@pytest.mark.asyncio
async def test_eventual_consistency():
    """Test if GET eventually returns the correct value after a delay."""
    client1 = KeyValueClient(["localhost:50051"])  # First node
    client2 = KeyValueClient(["localhost:50052"])  # Second node
    await client1.initialize()
    await client2.initialize()  

    await client1.put("eventual_key", "final_value")
    await asyncio.sleep(5)  # Simulating eventual consistency delay
    value = await client2.get("eventual_key")

    assert value == "final_value", f"Expected 'final_value', got '{value}'"

