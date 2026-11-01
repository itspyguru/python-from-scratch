# python-load-balancer-health-checks

A small, from-scratch HTTP load balancer in Python, built as a teaching project: round-robin
routing across three backend copies of the same FastAPI app, plus a background health-check
loop that detects a dead backend and routes around it automatically.

This is the real code used in the "I Built a Load Balancer in Python (with Health Checks)"
video on [@itspyguru](https://github.com/itspyguru) — every line shown on screen is copied
verbatim from this repo.

## What's here

- `server.py` — the backend app. A small FastAPI app with two routes: `/` (returns a message
  and the server's own ID) and `/health` (a status check, meant for the balancer, not a human).
  The same file runs as three different-looking servers just by setting a `SERVER_ID`
  environment variable and a different port.
- `balancer.py` — the load balancer. Round-robins requests across the three backends using
  `itertools.cycle`, proxies every request/response (headers, body, status code) with a shared
  `httpx.AsyncClient`, and runs a background loop that polls each backend's `/health` route
  every 5 seconds, pulling a dead backend out of rotation and putting a recovered one back in.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn httpx

# three backend copies, one per terminal
SERVER_ID=server-1 uvicorn server:app --port 8001
SERVER_ID=server-2 uvicorn server:app --port 8002
SERVER_ID=server-3 uvicorn server:app --port 8003

# the balancer, in front of them
uvicorn balancer:app --port 8000
```

Then hit `http://127.0.0.1:8000/` repeatedly — each request round-robins across the three
backends. Kill one of the backend processes and keep hitting the balancer: you'll see one
`502` right away (round robin doesn't know yet), then clean responses from the two survivors
once the next health check (within 5 seconds) notices and removes it. Bring the backend back
and it rejoins the rotation within one more health-check cycle.

## What this is not

This is a teaching build, not a production load balancer. No TLS termination, no streaming
support, no WebSockets, no rate limiting or metrics, no shared state across multiple balancer
processes, and a known bug (it forwards the backend's original `Content-Encoding` header even
though `httpx` already decompressed the body). All of this is covered — including the fix —
in the video.

## License

MIT — do whatever you like with it.
