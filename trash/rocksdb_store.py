import rocksdb

class RocksDBStore:
    def __init__(self, db_path="kvstore.db"):
        self.db = rocksdb.DB(db_path, rocksdb.Options(create_if_missing=True))

    def put(self, key: str, value: str) -> str:
        """Stores a key-value pair and returns the old value if it existed."""
        old_value = self.get(key)
        self.db.put(key.encode(), value.encode())
        return old_value

    def get(self, key: str) -> str:
        """Retrieves the value associated with a key."""
        value = self.db.get(key.encode())
        return value.decode() if value else ""

    def delete(self, key: str) -> None:
        """Deletes a key from the store."""
        self.db.delete(key.encode())

    def list_keys(self) -> list:
        """Returns a list of all keys in the store."""
        keys = []
        it = self.db.iterkeys()
        it.seek_to_first()
        for key in it:
            keys.append(key.decode())
        return keys

    def backup(self, backup_path="kvstore_backup") -> bool:
        """Creates a backup of the database."""
        try:
            checkpoint = rocksdb.Checkpoint(self.db)
            checkpoint.create_checkpoint(backup_path)
            print("Backup successful!")  # Force success message
            sys.stdout.flush()
            return True
        except Exception as e:
            error_message = f"Backup failed: {e}"  # Capture error message
            print(error_message)
            sys.stdout.flush()
            return False

# Testing the storage layer
if __name__ == "__main__":
    store = RocksDBStore()
    print("Putting key 'foo' -> 'bar'")
    old_value = store.put("foo", "bar")
    print(f"Old value: {old_value}")
    
    print("Getting key 'foo'")
    value = store.get("foo")
    print(f"Value: {value}")
    
    print("Listing keys")
    keys = store.list_keys()
    print(f"Keys: {keys}")
    
    print("Deleting key 'foo'")
    store.delete("foo")
    
    print("Creating backup")
    success = store.backup()
    print(f"Backup Status: {success}")
