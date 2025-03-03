import asyncio
import logging
import signal
import sys
import os

# Ensure the server module is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import client
from client.kv_client import KeyValueClient

def signal_handler(signum, frame):
    """Handles exit signal to gracefully terminate the CLI."""
    print("\nExiting CLI...")
    exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)

async def interactive_cli():
    """Interactive command-line interface for sending requests to the key-value store."""
    client = KeyValueClient(["localhost:50051", "localhost:50052", "localhost:50053"])
    await client.initialize()

    print("\nDistributed Key-Value Store CLI\n")
    print("Commands:")
    print("  put <key> <value>  - Store a key-value pair")
    print("  get <key>          - Retrieve the value of a key")
    print("  exit               - Quit the CLI\n")

    while True:
        try:
            user_input = input("kvstore> ").strip().split(" ", 2)
            if not user_input:
                continue
            
            command = user_input[0].lower()
            
            if command == "put" and len(user_input) == 3:
                key, value = user_input[1], user_input[2]
                old_value = await client.put(key, value)
                print(f"Old Value: {old_value if old_value else 'None'}")
            
            elif command == "get" and len(user_input) == 2:
                key = user_input[1]
                value = await client.get(key)
                print(f"Value: {value if value else 'Key not found'}")
            
            elif command == "exit":
                print("Exiting...")
                break
            
            else:
                print("Invalid command. Use 'put <key> <value>' or 'get <key>' or 'exit'.")

        except Exception as e:
            logging.error(f"Error: {e}")

    await client.kv_shutdown()

if __name__ == "__main__":
    asyncio.run(interactive_cli())
