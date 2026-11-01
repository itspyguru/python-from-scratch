import time

from cache import SimpleCache

cache = SimpleCache()
cache.set("user:101", "Asha", ttl=3)
print("now:", cache.get("user:101"))
time.sleep(4)
print("after 4 s:", cache.get("user:101"))
