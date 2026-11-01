from cache import LRUCache

cache = LRUCache(max_keys=2)
cache.set("a", 1)
cache.set("b", 2)
cache.get("a")
cache.set("c", 3)
print("keys:", list(cache.store))
