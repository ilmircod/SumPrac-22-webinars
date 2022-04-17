from datetime import datetime

from aredis_om import JsonModel

from models.base import BaseOrjsonModel


class Device(JsonModel):
    battery_level: float
    battery_level_updated_at: datetime

    class Config(BaseOrjsonModel.Config):
        pass
