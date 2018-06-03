import os

import aiohttp
from asyncinit import asyncinit
from aiogcd.connector import GcdServiceAccountConnector as Connector
from aiogcd.connector import entity


@asyncinit
class Data:
    async def __init__(self, datastore_project_id: str, datastore_credentials: str, session: aiohttp.ClientSession):
        self._client: Connector = await self._create_datastore_client(
            datastore_project_id, datastore_credentials, session)
        await self._setup_datastore()

    async def _create_datastore_client(self, project_id: str, credentials: str,
                                       session: aiohttp.ClientSession) -> Connector:
        tempfile_name = 'datastore_keys.temp'
        with open(tempfile_name, mode='w', encoding='utf8') as keys:
            keys.write(credentials)
        connector = Connector(project_id, tempfile_name, session)
        await connector.connect()
        os.remove(tempfile_name)
        return connector

    async def _setup_datastore(self):
        users_root_entity = entity.Entity({
            'key': {
                'partitionId': {
                    'projectId': self._client.project_id
                },
                'path': [
                    {
                        'kind': 'Users',
                        'name': 'users'
                    }
                ]
            },
            'properties': { }
        })
        await self._client.insert_entity(users_root_entity)

