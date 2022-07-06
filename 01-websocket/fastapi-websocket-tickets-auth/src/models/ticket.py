import uuid

from aredis_om import JsonModel

from models.base import BaseOrjsonModel


class Ticket(JsonModel):
    user_uuid: uuid.UUID
    measurement_uuid: uuid.UUID

    class Config(BaseOrjsonModel.Config):
        pass
