from cache import MISSING, SimpleCache

cache = SimpleCache()
cache.set("user:999", None, ttl=30)
print("plain get:", cache.get("user:999"))
print("never set:", cache.get("user:000"))
print("cached?", cache.get("user:999", MISSING) is not MISSING)
print("cached?", cache.get("user:000", MISSING) is not MISSING)
