from typing import Final

VERSION: Final = "2.0.8"
FLOW_VERSION = "1" 

DOMAIN: Final = "emcd_pool"

DEFAULT_NAME: Final = "EMCD"

SCAN_INTERVAL: Final = 5

DATA_EMCD: Final = "emcd_pool_cache"

DATA_YAML_CONFIG: Final = DOMAIN + "_yaml_config"
DATA_FINAL_CONFIG: Final = DOMAIN + "_final_config"
DATA_ENTITIES: Final = DOMAIN + "_entities"
DATA_UPDATERS: Final = DOMAIN + "_updaters"
DATA_UPDATE_LISTENERS: Final = DOMAIN + "_update_listeners"

CLIENT_API_URL: Final = "https://api.emcd.io"
CLIENT_API_VERSION: Final = "v1"
CLIENT_REQUEST_TIMEOUT: Final = 10
CLIENT_USER_AGENT: Final = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"

CONF_COINS: Final = "coins"
CONF_ACCOUNT: Final = "account"

ATTRIBUTION: Final = 'Data provided by EMCD'

ATTR_COIN: Final = "coin"
ATTR_ACCOUNT: Final = "account"
ATTR_TIMESTAMP: Final = "unix timestamp"
ATTR_DATETIME: Final = "datetime"

ATTR_TOTAL_PAID: Final = "total_paid"
ATTR_BALANCE: Final = "balance"
ATTR_PAYOUT_ADDRESS: Final = "payout_address"
ATTR_MIN_PAYOUT: Final = "min_payout"

ATTR_STATUS_HRATE: Final = "hashrate"
ATTR_STATUS_HRATE1H: Final = "average hashrate (1 hour)"
ATTR_STATUS_HRATE24H: Final = "average hashrate (24 hours)"
ATTR_STATUS_ALL_WORKERS: Final = "all workers"
ATTR_STATUS_VALID_WORKERS: Final = "valid workers"
ATTR_STATUS_INVALID_WORKERS: Final = "invalid workers"
ATTR_STATUS_INACTIVE_WORKERS: Final = "inactive workers"
ATTR_STATUS_UNKNOWN_WORKERS: Final = "unknown workers"
ATTR_STATUS_TOTAL_ALERTS: Final = "All workers with alerts"

ATTR_WORKER_STATUS: Final = "status"
ATTR_WORKER_WORKER: Final = "worker_name"

ATTR_REWARDS_INCOME: Final = "income"
ATTR_REWARDS_TYPE: Final = "reward type"
ATTR_REWARDS_HASHRATE: Final = "total hashrate"

ATTR_PAYOUTS_AMOUNT: Final = "amount"
ATTR_PAYOUTS_TXID: Final = "transaction id"

COIN_ICONS: Final = {
    "BTC": "mdi:currency-btc",
    "LTC": "mdi:litecoin",
    "BCH": "mdi:bitcoin",
    "BSV": "mdi:bitcoin",
    "ETH": "mdi:ethereum",
    "ETC": "mdi:ethereum",
}
COIN_EMCD: Final = {
    'bitcoin': 'btc',
    'bitcoin_cash': 'btc',
    'bitcoin_sv': 'bsv',
    'litecoin': 'ltc'     
}