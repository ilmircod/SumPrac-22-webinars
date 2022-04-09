from fastapi import APIRouter

from api.v1.endpoints import measurement, ticket

api_router = APIRouter()

api_router.include_router(ticket.router, tags=["ticket"])
api_router.include_router(measurement.router, tags=["measurement"])
