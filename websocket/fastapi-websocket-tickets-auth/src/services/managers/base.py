import uuid
from typing import Union

from aredis_om import NotFoundError
from fastapi import HTTPException


class BaseManager:
    instance_id: Union[uuid.UUID, str]
    instance_schema = None
    instance_verbose_name = None

    async def get(self):
        cached_instance = await self._get_from_db()
        if not cached_instance:
            external_instance = await self._get_from_api()
            if not external_instance:
                raise HTTPException(status_code=404, detail=f"{self.instance_verbose_name} not found")
            cached_instance = await self.save(instance=external_instance)
        return cached_instance

    @staticmethod
    async def save(instance):
        return await instance.save()

    async def _get_from_db(self):
        try:
            return await self.instance_schema.get(self.instance_id)
        except NotFoundError:
            pass

    async def _get_from_api(self):
        raise NotImplementedError
