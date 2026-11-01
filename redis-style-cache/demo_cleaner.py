import time

from cache import SimpleCache

cache = SimpleCache()
for i in range(1000):
    cache.set(f"key:{i}", i, ttl=1)
time.sleep(1.1)
print("all expired, still stored:", len(cache.store))
cache.start_cleaner(every=0.5)
time.sleep(1)
print("after the cleaner:", len(cache.store))
cache.stop_cleaner()
print("cleaner stopped:", cache.cleaner is None)
