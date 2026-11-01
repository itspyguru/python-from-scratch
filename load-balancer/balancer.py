import asyncio
from contextlib import asynccontextmanager
from itertools import cycle

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

BACKENDS = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003",
]

backend_cycle = cycle(BACKENDS)
backend_lock = asyncio.Lock()
healthy_backends = set(BACKENDS)
client = None

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
}

async def health_check_loop():
    while True:
        for backend in BACKENDS:
            try:
                response = await client.get(
                    f"{backend}/health",
                    timeout=2.0,
                )

                if response.is_success:
                    healthy_backends.add(backend)
                else:
                    healthy_backends.discard(backend)

            except httpx.RequestError:
                healthy_backends.discard(backend)

        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client

    client = httpx.AsyncClient(
        timeout=httpx.Timeout(5.0)
    )

    health_task = asyncio.create_task(
        health_check_loop()
    )

    try:
        yield
    finally:
        health_task.cancel()

        try:
            await health_task
        except asyncio.CancelledError:
            pass

        await client.aclose()
        client = None

app = FastAPI(lifespan=lifespan)

async def get_next_backend():
    async with backend_lock:
        for _ in range(len(BACKENDS)):
            backend = next(backend_cycle)

            if backend in healthy_backends:
                return backend

    raise HTTPException(
        status_code=503,
        detail="No healthy backend servers available",
    )

@app.api_route(
    "/{path:path}",
    methods=[
        "GET", "POST", "PUT", "PATCH",
        "DELETE", "OPTIONS", "HEAD",
    ],
)
async def load_balance(path: str, request: Request):
    backend = await get_next_backend()

    target_url = f"{backend}/{path}"

    if request.url.query:
        target_url += f"?{request.url.query}"

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    try:
        upstream = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail=f"Backend request failed: {backend}",
        )

    response_headers = {
        key: value
        for key, value in upstream.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
        and key.lower() != "content-length"
    }

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )
