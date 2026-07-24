class MemoryCache:
    """
    Simple in-memory cache for storing
    question-answer pairs.
    """

    def __init__(self):
        self.cache = {}

    def get(self, key):
        if not key:
            return None

        return self.cache.get(key)

    def set(self, key, value):
        if not key:
            return

        self.cache[key] = value

    def delete(self, key):
        if not key:
            return

        self.cache.pop(key, None)

    def clear(self):
        self.cache.clear()

    def contains(self, key):
        if not key:
            return False

        return key in self.cache

    def size(self):
        return len(self.cache)