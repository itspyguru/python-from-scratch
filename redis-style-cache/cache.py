import threading
import time
from collections import OrderedDict

MISSING = object()


class SimpleCache:
    def __init__(self):
        self.store = {}
        self.lock = threading.RLock()
        self.key_locks = {}
        self.cleaner = None
        self.stop_event = threading.Event()

    def _expired(self, entry):
        at = entry["expires_at"]
        return at is not None and time.monotonic() >= at

    def set(self, key, value, ttl=None):
        at = None
        if ttl is not None:
            at = time.monotonic() + ttl
        with self.lock:
            self.store[key] = {"value": value, "expires_at": at}

    def get(self, key, default=None):
        with self.lock:
            entry = self.store.get(key)
            if entry is None:
                return default
            if self._expired(entry):
                del self.store[key]
                return default
            return entry["value"]

    def delete(self, key):
        with self.lock:
            return self.store.pop(key, MISSING) is not MISSING

    def expire(self, key, ttl):
        with self.lock:
            entry = self.store.get(key)
            if entry is None or self._expired(entry):
                self.store.pop(key, None)
                return False
            entry["expires_at"] = time.monotonic() + ttl
            return True

    def clear(self):
        with self.lock:
            self.store.clear()

    def cleanup(self):
        with self.lock:
            dead = [
                k for k, e in self.store.items()
                if self._expired(e)
            ]
            for key in dead:
                del self.store[key]
            return len(dead)

    def start_cleaner(self, every=1.0):
        if self.cleaner is not None:
            return

        def loop():
            while not self.stop_event.wait(every):
                self.cleanup()

        self.cleaner = threading.Thread(target=loop, daemon=True)
        self.cleaner.start()

    def stop_cleaner(self):
        if self.cleaner is None:
            return
        self.stop_event.set()
        self.cleaner.join()
        self.cleaner = None
        self.stop_event.clear()

    def get_or_load(self, key, loader, ttl=None):
        value = self.get(key, MISSING)
        if value is not MISSING:
            return value
        with self.lock:
            key_lock = self.key_locks.setdefault(
                key, threading.Lock()
            )
        with key_lock:
            value = self.get(key, MISSING)
            if value is not MISSING:
                return value
            value = loader()
            self.set(key, value, ttl)
            return value


class LRUCache(SimpleCache):
    def __init__(self, max_keys):
        if max_keys < 1:
            raise ValueError("max_keys must be at least 1")
        super().__init__()
        self.store = OrderedDict()
        self.max_keys = max_keys

    def get(self, key, default=None):
        with self.lock:
            value = super().get(key, default)
            if key in self.store:
                self.store.move_to_end(key)
            return value

    def set(self, key, value, ttl=None):
        with self.lock:
            super().set(key, value, ttl)
            self.store.move_to_end(key)
            while len(self.store) > self.max_keys:
                self.store.popitem(last=False)
