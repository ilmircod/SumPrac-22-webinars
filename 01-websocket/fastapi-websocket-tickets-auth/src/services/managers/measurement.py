import dataclasses
import uuid
from typing import Optional

import aiohttp
from loguru import logger

from core.config import settings
from models.measurement import Measurement
from services.managers.base import BaseManager


@dataclasses.dataclass
class MeasurementManager(BaseManager):
    instance_id: uuid.UUID
    instance_schema = Measurement
    instance_verbose_name: str = "Measurement"
    context: dict = dict

    # TODO: backoff
    async def _get_from_api(self) -> Optional[Measurement]:
        # headers = {"Authorization": self.context["auth_token"]}
        # async with aiohttp.ClientSession(headers=headers) as session:
        #     url = settings.backend_url + f"api/v1/measurement/{str(self.instance_id)}/"
        #     async with session.get(url) as response:
        #         logger.info(f"GET {url}")
        #         if response.ok:
        #             _raw = await response.json()
        #             _data = {"pk": _raw["id"], "device_uuid": _raw["device"]}
        #             return self.instance_schema(**_data)

        logger.info(f"External API call [{self.__class__.__name__}]")
        _raw = {"id": "34407d2c-24a8-4aae-895a-f3760f0932d4", "device": "957c80d6-d080-4fbe-bc81-a2b5a97e3601"}
        _data = {"pk": _raw["id"], "device_uuid": _raw["device"]}
        return self.instance_schema(**_data)