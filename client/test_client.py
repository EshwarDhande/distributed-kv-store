import asyncio
from client.kv_client import KeyValueClient

async def test_grpc_connection():
    client = KeyValueClient("localhost:50051")

    print("🚀 Testing PUT operation...")
    old_value = await client.put("test_key", "test_value")
    print(f"PUT Response: Old Value -> {old_value}")

    print("🔍 Testing GET operation...")
    value = await client.get("test_key")
    print(f"GET Response: Value -> {value}")

    print("🗑️ Testing DELETE operation...")
    await client.delete("test_key")
    print("DELETE operation successful.")

    print("📜 Testing LIST operation...")
    keys = await client.list_keys()
    print(f"LIST Response: {keys}")

    await client.backup()
    print("💾 Backup operation triggered.")

    await client.channel.close()  # Ensure proper cleanup

if __name__ == "__main__":
    asyncio.run(test_grpc_connection())
