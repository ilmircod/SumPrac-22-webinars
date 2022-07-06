import dataclasses
import uuid
from typing import Optional

import aiohttp
from loguru import logger

from core.config import settings
from models.user import User
from services.managers.base import BaseManager


@dataclasses.dataclass
class UserManager(BaseManager):
    instance_id: uuid.UUID
    instance_schema = User
    instance_verbose_name: str = "User"
    context: dict = dict

    # TODO: backoff
    async def _get_from_api(self) -> Optional[User]:
        # headers = {"Authorization": self.context["auth_token"]}
        # async with aiohttp.ClientSession(headers=headers) as session:
        #     url = settings.backend_url + "api/v1/user/"
        #     async with session.get(url) as response:
        #         logger.info(f"GET {url}")
        #         if response.ok:
        #             _raw = await response.json()
        #             _data = {"pk": _raw["id"]}
        #             return self.instance_schema(**_data)

        logger.info(f"External API call [{self.__class__.__name__}]")
        _raw = {"id": "6663fd5e-c2ac-4824-9ab2-0612561f3f41"}
        _data = {"pk": _raw["id"]}
        return self.instance_schema(**_data)
