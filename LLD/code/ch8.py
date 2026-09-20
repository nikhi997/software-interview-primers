class LoggerStorage:
    def __init__(self, inner_storage):
        self.inner = inner_storage

    def load(self):
        print("Loading data from LoggerStorage")
        return self.inner.load()

    def save(self, data):
        print("Saving data to LoggerStorage")
        self.inner.save(data)

class CompressionStorage:
    def __init__(self, inner_storage):
        self.inner = inner_storage

    def load(self):
        print("Loading data from CompressionStorage")
        return self.inner.load()

    def save(self, data):
        print("Saving data to CompressionStorage")
        data = self._compress(data)
        self.inner.save(data)

    def _compress(self, data):
        gzip_data = f"compressed({data})"
        return gzip_data
class CachingStorage:
    def __init__(self, inner_storage):
        self.inner = inner_storage
        self.cache = None

    def load(self):
        if self.cache is not None:
            print("Loading data from cache")
            return self.cache
        print("Loading data from CachingStorage")
        self.cache = self.inner.load()
        return self.cache

    def save(self, data):
        print("Saving data to CachingStorage")
        self.inner.save(data)
        self.cache = data

import json


class EncryptedStorage:
    def __init__(self, inner_storage, key):
        self.inner = inner_storage
        self.key = key

    def save(self, data):
        encrypted = self._encrypt(data)
        self.inner.save(encrypted)

    def load(self):
        encrypted = self.inner.load()
        return self._decrypt(encrypted)

    def _encrypt(self, data):
        # toy XOR — DO NOT use for real secrets
        text = json.dumps(data)
        return {"_encrypted": [ord(char) ^ self.key for char in text]}

    def _decrypt(self, encrypted):
        if "_encrypted" not in encrypted:
            return encrypted
        text = "".join(chr(b ^ self.key) for b in encrypted["_encrypted"])
        return json.loads(text)


class LoggedStorage:
    def __init__(self, inner_storage, label="storage"):
        self.inner = inner_storage
        self.label = label

    def save(self, data):
        print(f"[{self.label}] saving {len(str(data))} bytes")
        self.inner.save(data)

    def load(self):
        print(f"[{self.label}] loading")
        return self.inner.load()
