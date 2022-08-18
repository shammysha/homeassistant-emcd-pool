"""
EMCD sensor
"""
from homeassistant.const import (
    ATTR_ATTRIBUTION
)

from homeassistant.core import ( 
    callback
)

from homeassistant.components.sensor import (
    SensorEntity
)

from homeassistant.util import (
    slugify
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)

from .const import (
    ATTRIBUTION,
    ATTR_COIN,
    ATTR_ACCOUNT,
    ATTR_TIMESTAMP,
    ATTR_DATETIME,
    ATTR_TOTAL_PAID,
    ATTR_BALANCE,
    ATTR_PAYOUT_ADDRESS,
    ATTR_MIN_PAYOUT,
    ATTR_STATUS_HRATE,
    ATTR_STATUS_HRATE1H,
    ATTR_STATUS_HRATE24H,
    ATTR_STATUS_ALL_WORKERS,
    ATTR_STATUS_VALID_WORKERS,
    ATTR_STATUS_INVALID_WORKERS,
    ATTR_STATUS_INACTIVE_WORKERS,
    ATTR_WORKER_STATUS,
    ATTR_WORKER_WORKER,
    ATTR_REWARDS_INCOME,
    ATTR_REWARDS_TYPE,
    ATTR_REWARDS_HASHRATE,
    ATTR_PAYOUTS_AMOUNT,
    ATTR_PAYOUTS_TXID,
    COIN_ICONS,
    DOMAIN,
    DEFAULT_NAME
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_id = config_entry.entry_id
    sensors = hass.data[DOMAIN][entry_id]['sensors']
    coordinator = hass.data[DOMAIN][entry_id]['coordinator']

    for sensor_data in sensors:
        sensor = False
        
        if sensor_data is None:
            continue

        elif all(i in sensor_data for i in ['coin', 'username', 'balance', 'total_paid', 'min_payout', 'address']):
            sensor = EMCDBalanceSensor(
                name = DEFAULT_NAME,
                coordinator = coordinator,
                coin = sensor_data['coin'],
                username = sensor_data['username'],
                balance = sensor_data['balance'],
                total_paid = sensor_data['total_paid'],
                min_payout = sensor_data['min_payout'],
                address = sensor_data['address']
            )

            
        elif all(i in sensor_data for i in ['name', 'coin', 'username', 'status', 'hashrate']):
            sensor = EMCDStatusSensor(
                name = DEFAULT_NAME,
                coordinator = coordinator,
                coin = sensor_data['coin'],
                username = sensor_data['username'],
                status = sensor_data['status'],
                hashrate = sensor_data['hashrate']
            )
            
        elif all(i in sensor_data for i in ['name', 'coin', 'username', 'worker', 'hashrate', 'hashrate1h', 'hashrate24h', 'active']):
            sensor = EMCDWorkerSensor(
                name = DEFAULT_NAME,
                coordinator = coordinator,
                coin = sensor_data['coin'],
                username = sensor_data['username'],
                worker = sensor_data['worker'],
                hashrate = sensor_data['hashrate'],
                hashrate1h = sensor_data['hashrate1h'],
                hashrate24h = sensor_data['hashrate24h'],
                active = sensor_data['active']
            )
    
        elif all(i in sensor_data for i in ['name', 'coin', 'username', 'timestamp', 'gmt_time', 'income', 'type', 'hashrate' ]):
            sensor = EMCDRewardsSensor(
                name = DEFAULT_NAME,
                coordinator = coordinator,
                coin = sensor_data['coin'],
                username = sensor_data['username'],
                timestamp = sensor_data['timestamp'],
                gmt_time = sensor_data['gmt_time'],
                income = sensor_data['income'],
                type = sensor_data['type'],
                hashrate = sensor_data['hashrate']
            )
                    
        elif all(i in sensor_data for i in ['name', 'coin', 'username', 'timestamp', 'gmt_time', 'amount', 'txid' ]):
            sensor = EMCDPayoutsSensor(
                name = DEFAULT_NAME,
                coordinator = coordinator,           
                coin = sensor_data['coin'],
                username = sensor_data['username'],
                timestamp = sensor_data['timestamp'],
                gmt_time = sensor_data['gmt_time'],
                amount = sensor_data['amount'],
                txid = sensor_data['txid']
            )        

        if sensor:
            async_add_entities([sensor], True)

class EMCDBalanceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, name, coin, username, address, balance, total_paid, min_payout):
        super().__init__(coordinator)        
        
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._name = f"{name} {username} ({coin}) info"
        self._coin = coin
        self._username = username
        self._balance = float(balance or 0.00)
        self._total_paid = float(total_paid or 0.00)
        self._min_payout = float(min_payout or 0.00)
        self._address = address
        self._unit_of_measurement = coin
        self._state = None

    @property
    def unique_id(self):
        return slugify(text = self._name, separator = '-')

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
            ATTR_BALANCE: "{:.8f}".format(self._balance),
            ATTR_TOTAL_PAID: "{:.8f}".format(self._total_paid),
            ATTR_MIN_PAYOUT: "{:.8f}".format(self._min_payout),            
            ATTR_PAYOUT_ADDRESS: f"{self._address}",
            ATTR_COIN: f"{self._coin}",
            ATTR_ACCOUNT: f"{self._username}"             
        }
        
        return data

    @callback
    def _handle_coordinator_update(self) -> None:
        self._balance = 0.00
        self._total_paid = 0.00
        self._min_payout = 0
        self._address = ''        
        
        if self._coin in self._coordinator.balances:
            self._balance = float(self._coordinator.balances[self._coin].get('balance') or 0.00)
            self._total_paid = float(self._coordinator.balances[self._coin].get('total_paid') or 0.00)
            self._min_payout = float(self._coordinator.balances[self._coin].get('min_payout') or 0.00)
            self._address = (self._coordinator.balances[self._coin].get('address') or '')                
         
        self._state = float(self._balance)     
 
        self.async_write_ha_state()
 
class EMCDStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, name, coin, username, status, hashrate):
        super().__init__(coordinator)        
        
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._name = f"{name} {username} ({coin}) status"
        self._coin = coin
        self._username = username
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
    def unique_id(self):
        return slugify(text = self._name, separator = '-')

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
            ATTR_ACCOUNT: f"{self._username}" 
        }
        
        return data

    @callback
    def _handle_coordinator_update(self) -> None:
        self._hrate = 0
        self._hrate1h = 0
        self._hrate24h = 0
        self._all_workers = 0
        self._valid_workers = 0
        self._invalid_workers = 0
        self._inactive_workers = 0       
        
        if self._coin in self._coordinator.mining:
            if 'status' in self._coordinator.mining[self._coin]:
                self._all_workers = self._coordinator.mining[self._coin]['status'].get('all', 0)
                self._valid_workers = self._coordinator.mining[self._coin]['status'].get('active', 0)
                self._invalid_workers = self._coordinator.mining[self._coin]['status'].get('dead_count', 0)
                self._inactive_workers = self._coordinator.mining[self._coin]['status'].get('inactive', 0)                      
                
            if 'hashrate' in self._coordinator.mining[self._coin]:
                self._hrate = self._coordinator.mining[self._coin]['hashrate'].get('hashrate', 0)
                self._hrate1h = self._coordinator.mining[self._coin]['hashrate'].get('hashrate1h', 0)
                self._hrate24h = self._coordinator.mining[self._coin]['hashrate'].get('hashrate24h', 0)
         
        self._state = self._hrate 
 
        self.async_write_ha_state()
 
class EMCDWorkerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, name, coin, username, worker, hashrate, hashrate1h, hashrate24h, active):
        super().__init__(coordinator)
        
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._name = f"{name} {username}.{worker} ({coin}) worker"
        self._coin = coin
        self._username = username
        self._worker = worker
        self._hrate = hashrate
        self._hrate1h = hashrate1h
        self._hrate24h = hashrate24h
        self._active = (active or 0)
        self._unit_of_measurement = "H/s"
        self._state = None

        self._status_vars = ["inactive", "valid"]
        self._status_icons = ["mdi:server-network-off", "mdi:server-network"]


    @property
    def unique_id(self):
        return slugify(text = self._name, separator = '-')
    
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
        except KeyError:
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
            ATTR_ACCOUNT: f"{self._username}" 
        }
        
        return data

    @callback
    def _handle_coordinator_update(self) -> None:
        self._hrate = 0
        self._hrate1h = 0
        self._hrate24h = 0
        self._active = 0
        
        if self._coin in self._coordinator.mining:
            if 'workers' in self._coordinator.mining[self._coin]:
                for worker in self._coordinator.mining[self._coin]['workers']:
                    if self._worker == worker['worker']:
                        self._hrate = worker.get('hashrate', 0)
                        self._hrate1h = worker.get('hashrate1h', 0)
                        self._hrate24h = worker.get('hashrate24h', 0)
                        self._active = (worker.get('active') or 0)
                            
         
        self._state = self._hrate 
        
        self.async_write_ha_state()
        
class EMCDRewardsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, name, coin, username, timestamp, gmt_time, rew_type, hashrate, income):
        super().__init__(coordinator)
        
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._name = f"{name} {username} ({coin}) rewards"
        self._coin = coin
        self._username = username
        self._timestamp = timestamp
        self._gmt_time = gmt_time
        self._income = float(income or 0.00)
        self._type = rew_type
        self._hashrate = hashrate
        self._unit_of_measurement = coin
        self._state = None


    @property
    def unique_id(self):
        return slugify(text = self._name, separator = '-')
    
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
            ATTR_REWARDS_INCOME: "{:.8f}".format(self._income),
            ATTR_REWARDS_HASHRATE: f"{self._hashrate}",
            ATTR_REWARDS_TYPE: f"{self._type}",
            ATTR_TIMESTAMP: f"{self._timestamp}",
            ATTR_DATETIME: f"{self._gmt_time}",
            ATTR_COIN: f"{self._coin}",
            ATTR_ACCOUNT: f"{self._username}"             
        }
        
        return data

    @callback
    def _handle_coordinator_update(self) -> None:        
        self._income = 0.00
        self._hashrate = 0

        if self._coin in self._coordinator.rewards:
            self._timestamp = self._coordinator.rewards[self._coin].get('timestamp', None)
            self._gmt_time = self._coordinator.rewards[self._coin].get('gmt_time', None)
            self._income = float(self._coordinator.rewards[self._coin].get('income', 0.00))
            self._type = self._coordinator.rewards[self._coin].get('type', None)
            self._hashrate = self._coordinator.rewards[self._coin].get('total_hashrate', 0)
         
        self._state = self._income             
        
        self.async_write_ha_state()
        
class EMCDPayoutsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, name, coin, username, timestamp, gmt_time, txid, amount):
        super().__init__(coordinator)
        
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._name = f"{name} {username} ({coin}) payouts"
        self._coin = coin
        self._username = username
        self._timestamp = timestamp
        self._gmt_time = gmt_time
        self._amount = float(amount or 0.00)
        self._txid = txid
        self._unit_of_measurement = coin
        self._state = None

    
    @property
    def unique_id(self):
        return slugify(text = self._name, separator = '-')

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
            ATTR_PAYOUTS_AMOUNT: "{:.8f}".format(self._amount),
            ATTR_PAYOUTS_TXID: f"{self._txid}",
            ATTR_TIMESTAMP: f"{self._timestamp}",
            ATTR_DATETIME: f"{self._gmt_time}",
            ATTR_COIN: f"{self._coin}",
            ATTR_ACCOUNT: f"{self._username}"             
        }
        
        return data

    @callback
    def _handle_coordinator_update(self) -> None:        
        self._amount = 0.00
        
        if self._coin in self._coordinator.payouts:
            self._timestamp = self._coordinator.payouts[self._coin].get('timestamp', None)
            self._gmt_time = self._coordinator.payouts[self._coin].get('gmt_time', None)
            self._amount = float(self._coordinator.payouts[self._coin].get('amount') or 0.00)
            self._txid = self._coordinator.payouts[self._coin].get('txid', None)                

        self._state = self._amount      
        
        self.async_write_ha_state()          