from cache import SimpleCache

cache = SimpleCache()


def broken():
    raise ConnectionError("database down")


try:
    cache.get_or_load("user:101", broken, ttl=30)
except ConnectionError as error:
    print("first call raised:", error)
print("cached?", "user:101" in cache.store)
value = cache.get_or_load("user:101", lambda: "Asha", ttl=30)
print("retry:", value)
