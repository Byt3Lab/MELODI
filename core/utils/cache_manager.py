class CacheManager:
    def __init__(self):
        pass

    def get(self, key):
        """
        Retrieve a value from the cache by its key.
        :param key: The key for the cached value.
        :return: The cached value or None if not found.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")
    
    def set(self, name, value):
        pass