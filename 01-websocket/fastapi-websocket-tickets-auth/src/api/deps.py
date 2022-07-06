import uuid

from fastapi import Depends, Query
from fastapi.security import APIKeyHeader
from starlette import status
from starlette.websockets import WebSocket

from models.user import User
from schemas.ticket import TicketInputSchema
from services.managers.measurement import MeasurementManager
from services.managers.token import AuthTokenManager
from services.managers.user import UserManager
from services.ws import WsTicketService

oauth2_scheme = APIKeyHeader(name="Token")


async def validate_ticket(websocket: WebSocket, measurement_uuid: uuid.UUID, ticket_value: str = Query(None)):
    ticket = await WsTicketService().validate(ticket_value=ticket_value, measurement_uuid=measurement_uuid)
    if not ticket:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return ticket


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    auth_token = await AuthTokenManager(instance_id=token).get()
    user = await UserManager(instance_id=auth_token.user_uuid, context={"auth_token": auth_token.pk}).get()
    return user


async def get_measurement(ticket: TicketInputSchema, token: str = Depends(oauth2_scheme)):
    auth_token = await AuthTokenManager(instance_id=token).get()
    measurement = await MeasurementManager(
        instance_id=ticket.measurement_uuid, context={"auth_token": auth_token.pk}
    ).get()
    return measurement
