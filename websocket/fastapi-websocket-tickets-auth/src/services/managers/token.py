import dataclasses
from typing import Optional

import aiohttp
from loguru import logger

from core.config import settings
from models.token import AuthToken
from models.user import User
from services.managers.base import BaseManager


@dataclasses.dataclass
class AuthTokenManager(BaseManager):
    instance_id: str
    instance_schema = AuthToken
    instance_verbose_name: str = "Auth Token"
    context: dict = dict

    # TODO: backoff
    async def _get_from_api(self) -> Optional[AuthToken]:
        # headers = {"Authorization": self.instance_id}
        # async with aiohttp.ClientSession(headers=headers) as session:
        #     url = settings.backend_url + "api/v1/user/"
        #     async with session.get(url) as response:
        #         logger.info(f"GET {url}")
        #         if response.ok:
        #             _raw = await response.json()
        #             _data = {"pk": self.instance_id, "user_uuid": _raw["id"]}
        #             await self._put_user_to_cache(_raw["id"])
        #             return self.instance_schema(**_data)

        logger.info(f"External API call [{self.__class__.__name__}]")
        _raw = {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}
        _data = {"pk": self.instance_id, "user_uuid": _raw["id"]}
        await self._put_user_to_cache(_raw["id"])
        return self.instance_schema(**_data)

    async def _put_user_to_cache(self, user_uuid) -> User:
        await User(pk=user_uuid).save()
