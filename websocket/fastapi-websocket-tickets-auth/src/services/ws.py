import dataclasses
import uuid
from typing import List

from aredis_om import NotFoundError
from starlette.websockets import WebSocket

from db.redis import get_redis
from enums.ws import WsActionEnum
from models.measurement import Measurement
from models.ticket import Ticket
from models.user import User
from schemas.ws import BaseWsMessage


@dataclasses.dataclass
class MeasurementWsHandler:
    message: BaseWsMessage
    measurement_uuid: uuid.UUID

    async def _handle_write_value(self):
        stream_key = f"measurement-stream:{str(self.measurement_uuid)}"
        payload = self.message.payload
        data = {"value": payload["value"], "timestamp": payload["timestamp"]}
        redis = await get_redis()
        await redis.xadd(stream_key, data)

    async def _handle_write_battery_level(self):
        # TODO: RedisStreams
        pass

    async def handle(self):
        ws_actions_map = {
            WsActionEnum.write_value: self._handle_write_value,
            WsActionEnum.write_battery_level: self._handle_write_battery_level,
        }
        await ws_actions_map[self.message.action]()


class WsTicketService:
    async def validate(self, ticket_value: str, measurement_uuid: uuid.UUID) -> bool:
        try:
            ticket = await Ticket.get(ticket_value)
        except NotFoundError:
            return False

        return ticket.measurement_uuid == measurement_uuid

    async def create(self, user: User, measurement: Measurement) -> Ticket:
        data = {
            "user_uuid": user.pk,
            "measurement_uuid": measurement.pk,
        }
        return await Ticket(**data).save()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
