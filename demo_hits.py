import time

import db
from cache import MISSING, SimpleCache

cache = SimpleCache()


def get_user(user_id):
    key = f"user:{user_id}"
    user = cache.get(key, MISSING)
    if user is not MISSING:
        print("CACHE HIT")
        return user
    print("CACHE MISS")
    user = db.fetch_user(user_id)
    cache.set(key, user, ttl=30)
    return user


for _ in range(3):
    start = time.perf_counter()
    get_user(101)
    print(f"{(time.perf_counter() - start) * 1000:.3f} ms")
print("database queries:", db.queries)
