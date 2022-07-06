import logging
import time

import aioredis
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from api.v1.api import api_router
from core.config import settings
from db import redis


app = FastAPI(
    title="Example WS Service",
    docs_url="/api/swagger",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = await aioredis.Redis(host=settings.redis_dsn.host, port=settings.redis_dsn.port)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()


app.include_router(api_router, prefix="/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8001, log_level=logging.INFO,
    )
