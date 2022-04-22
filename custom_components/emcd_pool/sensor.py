"""
EMCD sensor
"""
from datetime import datetime, timezone

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.components.sensor import SensorEntity

COIN_ICONS = {
    "BTC": "mdi:currency-btc",
    "LTC": "mdi:litecoin",
    "BCH": "mdi:bitcoin",
    "BSV": "mdi:bitcoin",
    "ETH": "mdi:etherium",
    "ETC": "mdi:etherium",
}

ATTRIBUTION = 'Data provided by EMCD'

ATTR_COIN = "coin"
ATTR_ACCOUNT = "account"

ATTR_TOTAL_PAID = "total_paid"
ATTR_BALANCE = "balance"
ATTR_PAYOUT_ADDRESS = "payout_address"
ATTR_MIN_PAYOUT = "min_payout"

ATTR_STATUS_HRATE = "hashrate"
ATTR_STATUS_HRATE1H = "average hashrate (1 hour)"
ATTR_STATUS_HRATE24H = "average hashrate (24 hours)"
ATTR_STATUS_ALL_WORKERS = "all workers"
ATTR_STATUS_VALID_WORKERS = "valid workers"
ATTR_STATUS_INVALID_WORKERS = "invalid workers"
ATTR_STATUS_INACTIVE_WORKERS = "inactive workers"
ATTR_STATUS_UNKNOWN_WORKERS = "unknown workers"
ATTR_STATUS_TOTAL_ALERTS = "All workers with alerts"

ATTR_WORKER_STATUS = "status"
ATTR_WORKER_WORKER = "worker_name"

ATTR_REWARDS_PREV = "previous reward"
ATTR_REWARDS_LAST = "last reward"

ATTR_PAYOUTS_PREV = "previous payout"
ATTR_PAYOUTS_LAST = "last payout"

DATA_EMCD = "emcd_pool_cache"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the Binance sensors."""

    if discovery_info is None:
        return
    
    elif all(i in discovery_info for i in ['name', 'coin', 'account', 'balance', 'total_paid', 'min_payout', 'address']):
        name = discovery_info['name']
        coin = discovery_info['coin']
        account = discovery_info['account']
        balance = discovery_info['balance']
        total_paid = discovery_info['total_paid']
        min_payout = discovery_info['min_payout']
        address = discovery_info['address']

        sensor = EMCDBalanceSensor(
            hass.data[DATA_EMCD], name, coin, account, balance, total_paid, min_payout, address
        )
        
    elif all(i in discovery_info for i in ['name', 'coin', 'account', 'status', 'hashrate']):
        name = discovery_info['name']
        coin = discovery_info['coin']
        account = discovery_info['account']
        status = discovery_info['status']
        hashrate = discovery_info['hashrate']

        sensor = EMCDStatusSensor(
            hass.data[DATA_EMCD], name, coin, account, status, hashrate
        )
        
    elif all(i in discovery_info for i in ['name', 'coin', 'account', 'worker', 'hashrate', 'hashrate1h', 'hashrate24h', 'active']):
        name = discovery_info['name']
        coin = discovery_info['coin']
        account = discovery_info['account']
        worker = discovery_info['worker']
        hashrate = discovery_info['hashrate']
        hashrate1h = discovery_info['hashrate1h']
        hashrate24h = discovery_info['hashrate24h']
        active = discovery_info['active']

        sensor = EMCDWorkerSensor(
            hass.data[DATA_EMCD], name, coin, account, worker, hashrate, hashrate1h, hashrate24h, active
        )

    elif all(i in discovery_info for i in ['name', 'coin', 'account', 'rewards']):
        name = discovery_info['name']
        coin = discovery_info['coin']
        account = discovery_info['account']
        rewards = discovery_info['rewards']

        sensor = EMCDRewardsSensor(
            hass.data[DATA_EMCD], name, coin, account, rewards
        )
        
    elif all(i in discovery_info for i in ['name', 'coin', 'account', 'payouts']):
        name = discovery_info['name']
        coin = discovery_info['coin']
        account = discovery_info['account']
        payouts = discovery_info['payouts']

        sensor = EMCDPayoutsSensor(
            hass.data[DATA_EMCD], name, coin, account, payouts
        )        

    async_add_entities([sensor], True)
    
    
class EMCDBalanceSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, emcd_data, name, coin, account, balance, total_paid, min_payout, address):
        """Initialize the sensor."""
        self._emcd_data = emcd_data
        self._name = f"{name} ({coin}) Info"
        self._coin = coin
        self._account = account
        self._balance = balance
        self._total_paid = total_paid
        self._min_payout = min_payout
        self._address = address
        self._unit_of_measurement = coin
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""

        return COIN_ICONS.get(self._coin, "mdi:currency-" + self._coin.lower())

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""

        data = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_BALANCE: "{:.8f}".format(float(self._balance)),
            ATTR_TOTAL_PAID: "{:.8f}".format(float(self._total_paid)),
            ATTR_MIN_PAYOUT: "{:.8f}".format(float(self._min_payout)),            
            ATTR_PAYOUT_ADDRESS: f"{self._address}",
            ATTR_COIN: f"{self._coin}",
            ATTR_ACCOUNT: f"{self._account}"             
        }
        
        return data

    async def async_update(self):
        """Update current values."""
        await self._emcd_data.async_update()
        
        self._balance = 0.00
        self._total_paid = 0.00
        self._min_payout = 0
        self._address = ''        
        
        if self._account in self._emcd_data.balances:
            if self._coin in self._emcd_data.balances[self._account]:
                self._balance = float(self._emcd_data.balances[self._account][self._coin]['balance'] or 0)
                self._total_paid = float(self._emcd_data.balances[self._account][self._coin]['balance'] or 0)
                self._min_payout = float(self._emcd_data.balances[self._account][self._coin]['balance'] or 0)
                self._address = (self._emcd_data.balances[self._account][self._coin]['balance'] or '')                
         
        self._state = float(self._balance)     
 
 
class EMCDStatusSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, emcd_data, name, coin, account, status, hashrate):
        """Initialize the sensor."""
        self._emcd_data = emcd_data
        self._name = f"{name} ({coin}) Status"
        self._coin = coin
        self._account = account
        self._hrate = hashrate.get('hashrate', 0)
        self._hrate1h = hashrate.get('hashrate1h', 0)
        self._hrate24h = hashrate.get('hashrate24h', 0)
        self._all_workers = status.get('all', 0)
        self._valid_workers = status.get('active', 0)
        self._invalid_workers = status.get('dead_count', 0)
        self._inactive_workers = status.get('inactive', 0)
        self._unit_of_measurement = "H/s"
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""

        return COIN_ICONS.get(self._coin, "mdi:currency-" + self._coin.lower())

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""

        data = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_STATUS_HRATE: f"{self._hrate}",
            ATTR_STATUS_HRATE1H: f"{self._hrate1h}",
            ATTR_STATUS_HRATE24H: f"{self._hrate24h}",
            ATTR_STATUS_ALL_WORKERS: f"{self._all_workers}",
            ATTR_STATUS_VALID_WORKERS: f"{self._valid_workers}",
            ATTR_STATUS_INVALID_WORKERS: f"{self._invalid_workers}",
            ATTR_STATUS_INACTIVE_WORKERS: f"{self._inactive_workers}",
            ATTR_COIN: f"{self._coin}",
            ATTR_ACCOUNT: f"{self._account}" 
        }
        
        return data

    async def async_update(self):
        """Update current values."""
        await self._emcd_data.async_update()
        
        self._hrate = 0
        self._hrate1h = 0
        self._hrate24h = 0
        self._all_workers = 0
        self._valid_workers = 0
        self._invalid_workers = 0
        self._inactive_workers = 0       
        
        if self._account in self._emcd_data.mining:
            if self._coin in self._emcd_data.mining[self._account]:
                if 'status' in self._emcd_data.mining[self._account][self._coin]:
                    self._all_workers = self._emcd_data.mining[self._account][self._coin]['status'].get('all', 0)
                    self._valid_workers = self._emcd_data.mining[self._account][self._coin]['status'].get('active', 0)
                    self._invalid_workers = self._emcd_data.mining[self._account][self._coin]['status'].get('dead_count', 0)
                    self._inactive_workers = self._emcd_data.mining[self._account][self._coin]['status'].get('inactive', 0)                      
                    
                if 'hashrate' in self._emcd_data.mining[self._account][self._coin]:
                    self._hrate = self._emcd_data.mining[self._account][self._coin]['hashrate'].get('hashrate', 0)
                    self._hrate1h = self._emcd_data.mining[self._account][self._coin]['hashrate'].get('hashrate1h', 0)
                    self._hrate24h = self._emcd_data.mining[self._account][self._coin]['hashrate'].get('hashrate24h', 0)
         
        self._state = self._hrate 
 
 
class EMCDWorkerSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, emcd_data, name, coin, account, worker, hashrate, hashrate1h, hashrate24h, active):
        """Initialize the sensor."""
        self._emcd_data = emcd_data
        self._name = f"{name}.{worker} ({coin}) worker"
        self._coin = coin
        self._account = account
        self._worker = worker
        self._hrate = hashrate
        self._hrate1h = hashrate1h
        self._hrate24h = hashrate24h
        self._active = active
        self._unit_of_measurement = "H/s"
        self._state = None

        self._status_vars = ["inactive", "valid"]
        self._status_icons = ["mdi:server-network-off", "mdi:server-network"]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""

        try:
            return self._status_icons[self._active]
        except KeyError as e:
            return self._status_icons[0]

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""

        data = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_STATUS_HRATE: f"{self._hrate}",
            ATTR_STATUS_HRATE1H: f"{self._hrate1h}",
            ATTR_STATUS_HRATE24H: f"{self._hrate24h}",
            ATTR_WORKER_STATUS: "{}".format(self._status_vars[self._active] or self._status_vars[0]),
            ATTR_WORKER_WORKER: f"{self._worker}",
            ATTR_COIN: f"{self._coin}",
            ATTR_ACCOUNT: f"{self._account}" 
        }
        
        return data

    async def async_update(self):
        """Update current values."""
        await self._emcd_data.async_update()
        
        self._hrate = 0
        self._hrate1h = 0
        self._hrate24h = 0
        self._active = 0
        
        if self._account in self._emcd_data.mining:
            if self._coin in self._emcd_data.mining[self._account]:
                if 'workers' in self._emcd_data.mining[self._account][self._coin]:
                    for worker in self._emcd_data.mining[self._account][self._coin]['workers']:
                        if self._worker == worker['worker']:
                            self._hrate = worker.get('hashrate', 0)
                            self._hrate1h = worker.get('hashrate1h', 0)
                            self._hrate24h = worker.get('hashrate24h', 0)
                            self._active = worker.get('active', 0)
                            
         
        self._state = self._hrate 
        
class EMCDRewardsSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, emcd_data, name, coin, account, rewards):
        """Initialize the sensor."""
        self._emcd_data = emcd_data
        self._name = f"{name} ({coin}) rewards"
        self._coin = coin
        self._account = account
        self._prev = rewards.get('previous', 0.00)
        self._last = rewards.get('last', 0.00)
        self._unit_of_measurement = coin
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""

        return COIN_ICONS.get(self._coin, "mdi:currency-" + self._coin.lower())

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""

        data = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_REWARDS_LAST: "{:.8f}".format(float(self._last)),
            ATTR_REWARDS_PREV: "{:.8f}".format(float(self._prev)),
            ATTR_COIN: f"{self._coin}",
            ATTR_ACCOUNT: f"{self._account}"             
        }
        
        return data

    async def async_update(self):
        """Update current values."""
        await self._emcd_data.async_update()
        
        self._prev = 0.00
        self._last = 0.00
        
        if self._account in self._emcd_data.rewards:
            if self._coin in self._emcd_data.rewards[self._account]:
                self._prev = self._emcd_data.rewards[self._account][self._coin].get('previous', 0.00)
                self._last = self._emcd_data.rewards[self._account][self._coin].get('last', 0.00)                
         
        self._state = float(self._last)             
        
        
class EMCDPayoutsSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, emcd_data, name, coin, account, payouts):
        """Initialize the sensor."""
        self._emcd_data = emcd_data
        self._name = f"{name} ({coin}) rewards"
        self._coin = coin
        self._account = account
        self._prev = payouts.get('previous', 0.00)
        self._last = payouts.get('last', 0.00)
        self._unit_of_measurement = coin
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""

        return COIN_ICONS.get(self._coin, "mdi:currency-" + self._coin.lower())

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""

        data = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_PAYOUTS_LAST: "{:.8f}".format(float(self._last)),
            ATTR_PAYOUTS_PREV: "{:.8f}".format(float(self._prev)),
            ATTR_COIN: f"{self._coin}",
            ATTR_ACCOUNT: f"{self._account}"             
        }
        
        return data

    async def async_update(self):
        """Update current values."""
        await self._emcd_data.async_update()
        
        self._prev = 0.00
        self._last = 0.00
        
        if self._account in self._emcd_data.payouts:
            if self._coin in self._emcd_data.payouts[self._account]:
                self._prev = self._emcd_data.payouts[self._account][self._coin].get('previous', 0.00)
                self._last = self._emcd_data.payouts[self._account][self._coin].get('last', 0.00)                

        self._state = float(self._last)                