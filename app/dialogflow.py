import asyncio
import json

import dialogflow
from google.oauth2.service_account import Credentials as GoogleCloudCredentials

from app.ratelimiter import RateLimiter


class Dialogflow:
    def __init__(self, credentials: str, loop: asyncio.AbstractEventLoop):
        parsed_credentials = json.loads(credentials)
        account = GoogleCloudCredentials.from_service_account_info(parsed_credentials)
        self._gcp_project_id: str = account.project_id
        self._loop: asyncio.AbstractEventLoop = loop
        self._session: dialogflow.SessionsClient = dialogflow.SessionsClient(credentials=account)
        self._rate_limeter: RateLimiter = RateLimiter(loop)

    async def detect_intent(self, message: str, user_id: int, channel_id: int = 0) -> str:
        self._rate_limeter.wait_before_request('request', 0.4)
        session_id = user_id * 10 + channel_id
        session = self._session.session_path(self._gcp_project_id, session_id)
        response = await self._loop.run_in_executor(None, self._session.detect_intent, session, message)
        return response.query_result
