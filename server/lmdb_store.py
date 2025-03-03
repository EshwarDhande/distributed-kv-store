import lmdb
import os
import kvstore_pb2
import shutil
import logging

class KeyValueStore:
    """Key-value store using LMDB."""
    
    def __init__(self, db_path="kvstore.lmdb", map_size=10485760):
        """Initialize LMDB with a fixed size."""
        self.env = lmdb.open(db_path, map_size=map_size, max_dbs=1)

    def put(self, key, value):
        """Store a key-value pair."""

        with self.env.begin(write=True) as txn:
            txn.put(key.encode(), value.encode())

    def get(self, key):
        """Retrieve a value for a given key."""

        with self.env.begin() as txn:
            value = txn.get(key.encode())

            if value is None:
                return ""  # Ensure a valid empty string instead of None

            try:
                return value.decode()  # Ensure bytes are converted to string
            except UnicodeDecodeError:
                logging.error(f"Invalid bytes stored for key '{key}': {value}")
                return ""

    def delete(self, key):
        """Delete a key-value pair."""

        with self.env.begin(write=True) as txn:
            txn.delete(key.encode())

    def list_keys(self):
        """Return all stored keys."""

        with self.env.begin() as txn:
            with txn.cursor() as cursor:
                return [key.decode() for key, _ in cursor]

    
    def backup(self, backup_path="lmdb_backup"):
        """Create a backup of the LMDB database."""

        try:

            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            os.makedirs(backup_path, exist_ok=True)

            # Correctly copy the database

            with self.env.begin(write=False) as txn:
                with open(os.path.join(backup_path, "backup.lmdb"), "wb") as f:
                    f.write(txn.get(b"backup") or b"")  # Ensure this is always bytes

            with self.env.begin(write=False) as txn:
                self.env.copy(backup_path, compact=True)
            
            response = kvstore_pb2.BackupStatus(success=True, message="Backup successful")
            print(f"DEBUG: Returning BackupStatus -> success: {response.success}, message: {response.message}")
            return response
        
        except lmdb.Error as e:
            response = kvstore_pb2.BackupStatus(success=False, message=f"Backup failed: {str(e)}")
            print(f"DEBUG: Returning BackupStatus -> success: {response.success}, message: {response.message}")
            return response
