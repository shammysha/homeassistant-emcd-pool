import json
import aiohttp
import asyncio
import requests
import time
import logging
import voluptuous as vol
from operator import itemgetter
from urllib.parse import urlencode
from homeassistant.const import CONF_API_KEY, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.util import Throttle

__version__ = "1.0.5"

DOMAIN = "emcd_pool"

DEFAULT_NAME = "EMCD"
CONF_API_KEY = "api_key"
CONF_COINS = "coins"

SCAN_INTERVAL = timedelta(minutes=1)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)
MIN_TIME_BETWEEN_MINING_UPDATES = timedelta(minutes=5)

DATA_EMCD = "emcd_pool_cache"

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Required(CONF_API_KEY): cv.string,
                vol.Optional(CONF_COINS, default=[]): vol.All(
                    cv.ensure_list, [cv.string]
                )
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    api_key = config[DOMAIN][CONF_API_KEY]
    name = config[DOMAIN].get(CONF_NAME)
    coins = config[DOMAIN].get(CONF_COINS)

    emcd_data = EMCDData(api_key)

    await emcd_data.async_update();

    hass.data[DATA_EMCD] = emcd_data

    for account, data in emcd_data.balances.items():
        for coin, balance in data.items():
            if coins and coin not in coins:
                continue

            balance['account'] = account
            balance['coin'] = coin.upper()
            balance['name'] = name

            await async_load_platform(hass, "sensor", DOMAIN, balance, config)

            if coin in emcd_data.mining[account]:
                status = {
                    'name': name,
                    'account': account,
                    'coin': coin.upper(),
                    'status': emcd_data.mining[account][coin]['status'],
                    'hashrate': emcd_data.mining[account][coin]['hashrate']
                }

                await async_load_platform(hass, "sensor", DOMAIN, status, config)

                for worker in emcd_data.mining[account][coin]['workers']:
                    worker['name'] = name
                    worker['account'] = account
                    worker['coin'] = coin.upper()

                    await async_load_platform(hass, "sensor", DOMAIN, worker, config)

            if coin in emcd_data.rewards:
                rewards['account'] = account
                rewards['coin'] = coin.upper()
                rewards['name'] = name
                rewards['rewards'] = emcd_data.rewards[account][coin]

                await async_load_platform(hass, "sensor", DOMAIN, rewards, config)

            if coin in emcd_data.rewards:
                payouts['account'] = account
                payouts['coin'] = coin.upper()
                payouts['name'] = name
                payouts['payouts'] = emcd_data.payouts[account][coin]

                await async_load_platform(hass, "sensor", DOMAIN, payouts, config)

    return True



class EMCDData:
    def __init__(self, api_key: str):
        self.client = EMCDPoolClient(api_key)
        self.coins = {
            'btc': 'bitcoin',
            'bch': 'bitcoin_cash',
            'bsv': 'bitcoin_sv',
            'ltc': 'litecoin'
        }
        self.account = None
        self.balances = {}
        self.mining = {}
        self.payouts = {}
        self.rewards = {}

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        _LOGGER.debug(f"Fetching data from api.emcd.io")

        balances = await self.client.async_get_info()
        if not balances:
            return False

        account = balances['username'];

        self.balances = {}
        self.balances[account] = {}
        self.mining[account] = {}
        self.payouts[account] = {}
        self.rewards[account] = {}

        for coin, data in balances.items():
            if coin in ['notifications', 'username']:
                continue

            for short_def, long_def in self.coins:
                if coin == long_def:
                    coin = short_def

            self.balances[account][coin] = data

            _LOGGER.debug(f"Balances updated from emcd.io")

        for coin in self.balances['accounts'][account]:

            workers = await self.client.async_get_workers(coin)
            if workers:
                self.mining[account][coin] = {
                    'status': workers['total_count'],
                    'hashrate': workers['total_hashrate'],
                    'workers': workers['details']
                }

                _LOGGER.debug(f"Workers updated from emcd.io")

            rewards = await self.client.async_get_rewards(coin)
            if rewards and 'income' in rewards:
                if len(rewards['income']) > 0:
                    self.rewards[account][coin]['last'] = (rewards['income'][0] or 0)
                if len(rewards['income']) > 1:
                    self.rewards[account][coin]['previous'] = rewards['income'][1]

                _LOGGER.debug(f"Rewards updated from emcd.io")

            payouts = await self.client.async_get_payouts(coin)
            if payouts and 'payouts' in payouts:
                if len(payouts['payouts']) > 0:
                    self.payouts[account][coin]['last'] = payouts['payouts'][0]
                if len(payouts['payouts']) > 1:
                    self.payouts[account][coin]['previous'] = payouts['payouts'][1]

                _LOGGER.debug(f"Payouts updated from emcd.io")

class EMCDPoolClient:
    API_URL = 'https://api.emcd.io'
    API_VERSION = 'v1'
    REQUEST_TIMEOUT = 10

    def __init__(self, api_key: str, loop = None):
        self.API_KEY = api_key
        self.session = self._init_session()
        self.response = None
        self.loop = loop or asyncio.get_event_loop()

    def _get_headers(self) -> Dict:
        return {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',  # noqa
        }

    def _init_session(self) -> aiohttp.ClientSession:
        session = aiohttp.ClientSession(
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

    async def _handle_response(self, response: aiohttp.ClientResponse):
        if not str(response.status).startswith('2'):
            raise EMCDAPIException(response, response.status, await response.text())
        try:
            return await response.json()
        except ValueError:
            txt = await response.text()
            raise EMCDRequestException(f'Invalid Response: {txt}')

    def _create_api_url(self, path: str, coin: str = None ) -> str:
        url = self.API_URL + '/' + self.API_VERSION
        if not coin is None:
            url += '/' + coin
        return url + '/' + path + '/' + self.API_KEY


    async def async_request_api(self, path: str, coin: str = None):
        uri = self._create_api_url(path, coin)

        answer = await self._request(uri)

        if 'code' in answer:
            _LOGGER.error(f"Error fetching data from api.emcd.io: {answer}")
            return False

        return answer

    async def async_get_info(self, path: str = 'info'):
        uri = self._create_api_url(path)

        return await self._request(uri)

    async def async_get_workers(self, coin, path: str = 'workers'):
        uri = self._create_api_url(path)

        return await self._request(uri)

    async def async_get_rewards(self, coin, path: str = 'income'):
        uri = self._create_api_url(path)

        return await self._request(uri)


    async def async_get_payouts(self, coin, path: str = 'payouts'):
        uri = self._create_api_url(path)

        return await self._request(uri)



class EMCDAPIException(Exception):

    def __init__(self, response, status_code, text):
        self.error = ''
        try:
            _LOGGER.debug(f"EMCDAPIException: {response} - {status_code}. {text}")
            json_res = json.loads(text)
        except ValueError:
            self.message = 'Invalid JSON error message from api.emcd.io: {}'.format(response.text)
        else:
            self.error = json_res.get("code", "")
            self.description = json_res.get("message", "")

        self.status_code = status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s. %s' % (self.status_code, self.error, self.description)


class EMCDRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'EMCDRequestException: %s' % self.message
