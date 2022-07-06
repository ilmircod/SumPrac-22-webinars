from pydantic import BaseModel

from enums.ws import WsActionEnum
from models.base import BaseOrjsonModel


class BaseWsMessage(BaseModel):
    action: WsActionEnum
    payload: dict

    class Config(BaseOrjsonModel.Config):
        pass
