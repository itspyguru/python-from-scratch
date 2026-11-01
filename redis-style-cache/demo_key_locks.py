from cache import SimpleCache

cache = SimpleCache()
for i in range(50_000):
    cache.get_or_load(f"user:{i}", lambda: i, ttl=0)
cache.cleanup()
print("cache entries:", len(cache.store))
print("key locks:", len(cache.key_locks))
