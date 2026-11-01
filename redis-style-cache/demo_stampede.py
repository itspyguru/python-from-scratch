from threading import Thread
import time

import db
from cache import MISSING, SimpleCache


def run(name, handler):
    db.queries = 0
    threads = [Thread(target=handler) for _ in range(1000)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    took = time.perf_counter() - start
    print(f"{name}: queries: {db.queries}, {took:.2f} s")


naive = SimpleCache()


def check_then_load():
    if naive.get("user:101", MISSING) is MISSING:
        naive.set("user:101", db.fetch_user(101), ttl=30)


run("check then load", check_then_load)
safe, key = SimpleCache(), "user:101"
load = lambda: db.fetch_user(101)
run("get_or_load", lambda: safe.get_or_load(key, load, ttl=30))
