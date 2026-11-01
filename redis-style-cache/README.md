# A Redis-style cache in Python

A small in-memory cache built from an empty file, line by line, for the itsPyguru video.
No dependencies: Python 3 standard library only.

- `cache.py`: `SimpleCache` (set, get, delete, expire, clear, cleanup, background cleaner, stampede-safe `get_or_load`) and `LRUCache`.
- `db.py`: a fake database that counts queries and sleeps 2 s.
- `demo_*.py`: one runnable demo per idea. Example: `python demo_stampede.py`.

Measured here with 1000 threads asking for one key: check-then-load made 1000 queries, `get_or_load` made 1.

This is a teaching build, not a Redis replacement. It is one process only, it scans every key while
cleaning, and `key_locks` never shrinks. For anything shared between processes, use Redis.
