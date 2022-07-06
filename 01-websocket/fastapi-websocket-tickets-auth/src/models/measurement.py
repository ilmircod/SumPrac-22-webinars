import uuid

from aredis_om import JsonModel

from models.base import BaseOrjsonModel


class Measurement(JsonModel):
    device_uuid: uuid.UUID

    class Config(BaseOrjsonModel.Config):
        pass
