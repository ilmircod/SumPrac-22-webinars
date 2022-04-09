import uuid

from pydantic import BaseModel

from models.base import BaseOrjsonModel


class TicketInputSchema(BaseModel):
    measurement_uuid: uuid.UUID

    class Config(BaseOrjsonModel.Config):
        pass
