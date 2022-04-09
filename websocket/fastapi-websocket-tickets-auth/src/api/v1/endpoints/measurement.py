import uuid

from fastapi import APIRouter, Depends, WebSocket
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from api.deps import validate_ticket
from schemas.ws import BaseWsMessage
from services.ws import MeasurementWsHandler, manager

router = APIRouter()


@router.websocket("/ws/measurement/{measurement_uuid}/")
async def measurement_ws(
    websocket: WebSocket, measurement_uuid: uuid.UUID, ticket_value: str = Depends(validate_ticket)  # noqa: B008
):
    if not ticket_value:
        return

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = BaseWsMessage.parse_raw(data)
                await MeasurementWsHandler(message=message, measurement_uuid=measurement_uuid).handle()
            except ValidationError as e:
                await manager.send_personal_message(str(e), websocket)
                raise WebSocketDisconnect

            await manager.send_personal_message(data, websocket)
            # TODO: broadcast message across the device channel
    except WebSocketDisconnect:
        manager.disconnect(websocket)
