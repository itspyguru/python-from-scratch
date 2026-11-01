import time

from cache import SimpleCache


def naive_expire(cache, key, ttl):
    if key not in cache.store:
        return False
    cache.store[key]["expires_at"] = time.monotonic() + ttl
    return True

versions = [("naive", naive_expire), ("ours", SimpleCache.expire)]
for name, expire in versions:
    cache = SimpleCache()
    cache.set("a", "old value", ttl=1)
    time.sleep(1.1)
    print(name, "expire:", expire(cache, "a", 100))
    print(name, "get:", cache.get("a"))
