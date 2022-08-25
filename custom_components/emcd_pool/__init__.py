import logging
import homeassistant.helpers.entity_registry as er

from asyncio import (
    gather
)
from datetime import (
    timedelta
)

from homeassistant.config_entries import (
    ConfigEntry, 
    SOURCE_IMPORT
)

from homeassistant.helpers.typing import (
    ConfigType, 
    HomeAssistantType
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity, 
    DataUpdateCoordinator, 
    UpdateFailed
)

from homeassistant.const import (
    CONF_API_KEY, 
    CONF_USERNAME
)

from homeassistant.exceptions import (
    ConfigEntryAuthFailed
)

from .client import (
    EMCDPoolClient
)

from .exceptions import (
    EMCDAPIException
)

from .util import (
    find_existing_entry, 
    async_fetch_username
)

from .schemas import (
    CONFIG_SCHEMA, 
    CONFIG_ENTRY_SCHEMA 
)

from .const import (
    FLOW_VERSION,
    DOMAIN, 
    DEFAULT_NAME, 
    SCAN_INTERVAL, 
    COIN_EMCD
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    domain_config = config.get(DOMAIN)
    
    if not domain_config:
        return True
    
    yaml_config = {}
    hass.data[DOMAIN] = { 'yaml': yaml_config }
    
    for item in domain_config:
        existing_entry = await find_existing_entry(hass, item[CONF_API_KEY])
        if existing_entry:
            if existing_entry.source == SOURCE_IMPORT:
                yaml_config[existing_entry.data[CONF_USERNAME]] = item
            
            continue
                
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=item
            )
        )        
    
    return True
    
async def async_setup_entry(hass: HomeAssistantType, config_entry: ConfigEntry) -> bool:   
    entry_id = config_entry.entry_id
    api_key = config_entry.data[CONF_API_KEY]
    
    try:
        username = config_entry.data[CONF_USERNAME]
    except (TypeError, ValueError, LookupError):
        username = await async_fetch_username(api_key)
        if not username:
            raise Exception('invalid credentials')

    config = {}
    
    if config_entry.source == SOURCE_IMPORT:
        yaml_config = hass.data[DOMAIN].get('yaml')
        
        if not (yaml_config and username in yaml_config):
            hass.async_create_task(hass.config_entries.async_remove(entry_id))
            return False
        
        config = yaml_config[username]
    
    else:
        config = CONFIG_ENTRY_SCHEMA({**config_entry.data, **config_entry.options})
    
    _LOGGER.debug(f"[{username}] Setting up config entry")
    
    emcd_data = EMCDData(hass, config[CONF_API_KEY])

    await emcd_data.async_config_entry_first_refresh()
    sensors = []

    for coin, balance in emcd_data.balances.items():
        balance['username'] = emcd_data.username
        balance['coin'] = coin

        sensors.append(balance)

        if mining := emcd_data.mining.get(coin, None):
            sensors.append({
                'username': emcd_data.username,
                'coin': coin,
                'status': mining['status'],
                'hashrate': mining['hashrate']
            })
        
            for worker in mining['workers']:
                sensors.append(worker.update({
                    'username': username,
                    'coin': coin
                }))


        if reward := emcd_data.rewards.get(coin, None):
            sensors.append({
                'username': username,
                'coin': coin,
                'timestamp': reward.get('timestamp', None),
                'gmt_time': reward.get('gmt_time', None),
                'income': reward.get('income', None),
                'type': reward.get('type', None),
                'hashrate': reward.get('total_hashrate', None)
            })
                
        if payout := emcd_data.payouts.get(coin, None):
            sensors.append({
                'username': username,
                'coin': coin,
                'timestamp': payout.get('timestamp', None),
                'gmt_time': payout.get('gmt_time', None),
                'amount': payout.get('amount', None),
                'txid': payout.get('txid', None)
            })

    hass.data.setdefault(DOMAIN, {})[entry_id] = {
        'config': config,
        'coordinator': emcd_data,
        'sensors': sensors
    }   

    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))

    if sensors:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
        )

    return True


async def async_unload_entry(hass, config_entry: ConfigEntry) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id]['coordinator']
    
    unload_ops = [
        hass.config_entries.async_forward_entry_unload(config_entry, "sensor"),
        coordinator.client.close_connection()
    ]

    onload_ok = all( [ await gather(*unload_ops) ] )
    if onload_ok:
        ent_reg = er.async_get(hass)
        for entity in er.async_entries_for_config_entry(ent_reg, config_entry.entry_id):
            if entity.entity_id.startswith('sensor'):
                ent_reg.async_remove(entity.entity_id)
    
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return onload_ok   

async def async_reload_entry(hass, config_entry: ConfigEntry) -> None:
    _LOGGER.info(f"[{config_entry.data[CONF_USERNAME]}] Reloading configuration entry")
    await hass.config_entries.async_reload(config_entry.entry_id)   
   

async def async_migrate_entry(hass, config_entry: ConfigEntry):
    _LOGGER.debug("Migrating from version %s to %s", config_entry.version, FLOW_VERSION)

    if config_entry.version != FLOW_VERSION:
        config_entry.version = FLOW_VERSION
        hass.config_entries.async_update_entry(config_entry, data={**config_entry.data})

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True  

class EMCDData(DataUpdateCoordinator):
    def __init__(self, hass, api_key: str):
        """Initialize."""
        
        super().__init__(hass, _LOGGER, name="EMCDData", update_interval=timedelta(minutes=SCAN_INTERVAL))
        
        self.client = EMCDPoolClient(api_key)
        self.username = None
        self.balances = {}
        self.mining = {}
        self.payouts = {}
        self.rewards = {}


    async def _async_update_data(self):
        _LOGGER.debug(f"Fetching data from api.emcd.io")
        
        try:
            balances = await self.client.async_get_info()
        
            if not balances:
                raise ConfigEntryAuthFailed(f'No data found for current API key')
    
            self.username = balances.pop('username', None);
            balances.pop('notifications', None);
            
            self.balances = {}
            self.mining = {}
            self.payouts = {}
            self.rewards = {}
    
            for coin, data in balances.items():
                coin = COIN_EMCD.get(coin, coin)
    
                self.balances[coin.upper()] = data
    
                _LOGGER.debug(f"Balances updated from emcd.io")
    
            for coin in self.balances:
                tasks = [
                    self.client.async_get_workers(coin.lower()),
                    self.client.async_get_rewards(coin.lower()),
                    self.client.async_get_payouts(coin.lower())
                ]
    
                res = await gather(*tasks, return_exceptions=True)
                
                workers, rewards, payouts = res
                
                if workers:
                    self.mining[coin] = {
                        'status': workers['total_count'],
                        'hashrate': workers['total_hashrate'],
                        'workers': workers['details']
                    }
                    _LOGGER.debug(f"Workers updated from emcd.io")
    
                self.rewards[coin] = {}
                if rewards and (reward := rewards.get('income', None)):
                    if len(reward) > 0:
                        self.rewards[coin] = reward[0]
                        
                    _LOGGER.debug(f"Rewards updated from emcd.io")
    
                self.payouts[coin] = {}
                if payouts and (payout := payouts.get('payouts', None)):
                    if len(payout) > 0:
                        self.payouts[coin] = payout[0]

                    _LOGGER.debug(f"Payouts updated from emcd.io")
        
        except EMCDAPIException as e:  
            await self.client.close_connection()  
            raise UpdateFailed from e
