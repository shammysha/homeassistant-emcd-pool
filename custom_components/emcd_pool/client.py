import logging
from aiohttp import ClientSession, ClientResponse
from asyncio import get_event_loop
from .exceptions import EMCDAPIException
from .const import (
     CLIENT_API_URL,
     CLIENT_API_VERSION,
     CLIENT_REQUEST_TIMEOUT,
     CLIENT_USER_AGENT
)
     
_LOGGER = logging.getLogger(__name__)     
     
class EMCDPoolClient:
    API_URL = CLIENT_API_URL
    API_VERSION = CLIENT_API_VERSION
    REQUEST_TIMEOUT = CLIENT_REQUEST_TIMEOUT
    USER_AGENT = CLIENT_USER_AGENT
    
    
    def __init__(self, api_key: str, loop = None):
        self.loop = loop or get_event_loop()
        self.API_KEY = api_key
        self.session = self._init_session()
        self.response = None

    @classmethod
    async def create(cls, api_key: str, loop=None):

        self = cls(api_key, loop)

        try:
            return self
        except Exception:
            # If ping throw an exception, the current self must be cleaned
            # else, we can receive a "asyncio:Unclosed client session"
            await self.close_connection()
            raise

    def _get_headers(self):
        return {
            'Accept': 'application/json',
            'User-Agent': CLIENT_USER_AGENT
        }

    def _init_session(self) -> ClientSession:
        session = ClientSession(
            loop=self.loop,
            headers=self._get_headers()
        )
        return session

    async def close_connection(self):
        if self.session:
            assert self.session
            await self.session.close()


    async def _request(self, uri: str):
        async with getattr(self.session, 'get')(uri) as response:
            self.response = response
            return await self._handle_response(response)

    async def _handle_response(self, response: ClientResponse):
        try:
            txt = await response.json()
        except ValueError:
            if response.status_code != 200:
                raise EMCDAPIException(response, response.status_code, await response.text())
            
            raise EMCDAPIException(response, response.status_code, await response.text())

        if 'error' in txt: 
            raise EMCDAPIException(response, response.status_code, txt.error)
        
        if 'code' in txt: 
            raise EMCDAPIException(response, response.status_code, f'{txt.code} - {txt.message}')
        
        return txt        

    def _create_api_url(self, path: str, coin: str = None ) -> str:
        url = CLIENT_API_URL + '/' + CLIENT_API_VERSION
        if coin:
            url += '/' + coin
        return url + '/' + path + '/' + self.API_KEY


    async def async_request_api(self, path: str, coin: str = None):
        uri = self._create_api_url(path, coin)

        answer = await self._request(uri)

        return answer

    async def async_get_info(self, path: str = 'info'):
        return await self.async_request_api(path)

    async def async_get_workers(self, coin, path: str = 'workers'):
        return await self.async_request_api(path, coin)

    async def async_get_rewards(self, coin, path: str = 'income'):
        return await self.async_request_api(path, coin)

    async def async_get_payouts(self, coin, path: str = 'payouts'):
        return await self.async_request_api(path, coin)