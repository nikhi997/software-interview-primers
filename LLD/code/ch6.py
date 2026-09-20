class Logger:
    _instance = None

    def __new__(cls, filename="app.log"):

        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.filename = filename
        elif cls._instance.filename != filename:
            raise ValueError("Logger instance already exists with a different filename.")
        return cls._instance

    def log(self, message):
        with open(self.filename, 'a') as f:
            f.write(message + '\n')


def create_storage(config):
        if config['type'] == "file":
            return FileStorage(config['filename'])
        elif config['type'] == "memory":
            return MemoryStorage()
        elif config['type'] == "redis":
            return RedisStorage(config["redis_client"])
        else:
            raise ValueError("Invalid storage type")

class FileStorage:
    def __init__(self, config):
        self.config = config
    def save(self, data):
        with open(self.config['filename'], 'w') as f:
            f.write(data)
    def load(self):
        with open(self.config['filename'], 'r') as f:
            return f.read()

class MemoryStorage:
    def __init__(self):
        self.storage = {}
    def save(self, key, data):
        self.storage[key] = data
    def load(self, key):
        return self.storage.get(key, None)

class RedisStorage:
    def __init__(self, redis_client):
        self.redis_client = redis_client
    def save(self, key, data):
        self.redis_client.set(key, data)
    def load(self, key):
        return self.redis_client.get(key)
