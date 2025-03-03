import asyncio
import logging
import sys
import os
# Ensure the server module is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import client
from client.kv_client import KeyValueClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def process_file(file_path):
    """Reads commands from a file and executes them in batch."""
    client = KeyValueClient(["localhost:50051", "localhost:50052", "localhost:50053"])
    await client.initialize()

    try:
        with open(file_path, "r") as file:
            commands = [line.strip().split(" ", 2) for line in file.readlines()]

        results = []
        for command in commands:
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == "put" and len(command) == 3:
                key, value = command[1], command[2]
                old_value = await client.put(key, value)
                results.append(f"PUT {key} -> Old Value: {old_value if old_value else 'None'}")
            
            elif cmd == "get" and len(command) == 2:
                key = command[1]
                value = await client.get(key)
                results.append(f"GET {key} -> Value: {value if value else 'Key not found'}")
            
            else:
                results.append(f"Invalid command: {' '.join(command)}")

        print("\nBatch Execution Results:")
        for result in results:
            print(result)
    
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except Exception as e:
        logging.error(f"Error processing file: {e}")
    finally:
        await client.kv_shutdown()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client_cli_batch.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    asyncio.run(process_file(input_file))
