# homeassistant-emcd-pool
EMCD pool statistics and monitoring

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

# EMCD Pool

### Installation with HACS
---
- Make sure that [HACS](https://hacs.xyz/) is installed
- Add the URL for this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) in HACS
- Install via `HACS -> Integrations`

### Usage
---
In order to use this integration, you need to first [Register an account with EMCD](https://emcd.io/pool/dashboard/registration), and then [get API-key](https://emcd.io/pool/dashboard/settings)  from bottom of "Settings" page.

To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
emcd_pool:
  api_key: !secret emcd_api_key
  
```

#### Configuration variables:
| Key               | Type   | Required | Description                               | Default |
| :---------------- | :----: | :------: |:--------------------------------------    | :-----: |
| `name`            | string | No       | Name for the created sensors              | EMCD    |
| `api_key`         | string | Yes      | Your's EMCD API key                       | -       |
| `coins`           | list   | No       | List of monitored coins                   | All     |

#### Full example configuration
```yaml
emcd_pool:
  name: my_emcd
  api_key: !secret emcd_api
  coins:
    - BTC
    - LTC
```

This configuration will create the following entities in your Home Assistant instance:
- Info sensors for each bundle (account + coin) with attributes...
  ```
  balance
  total paid
  min payout
  payout address
  coin
  account
  ```
  - "My EMCD username (BTC) Info" (`sensor.my_emcd_username_btc_info`)
  - "My EMCD username (LTC) Info" (`sensor.my_emcd_username_ltc_info`)

- Status sensors for each bundle (account + coin) with attributes...
  ```
  hashrate
  average hashrate (1 hour)
  average hashrate (24 hours)
  all workers
  valid workers
  invalid workers
  inactive workers
  coin
  account
  ```
  - "My EMCD username (BTC) Info" (`sensor.my_emcd_username_btc_status`)
  - "My EMCD username (LTC) Info" (`sensor.my_emcd_username_ltc_status`)  

- Worker's sensors for each bundle (account + coin + worker) with attributes...
  ```
  hashrate
  average hashrate (1 hour)
  average hashrate (24 hours)
  status (value can be "inactive" or "valid")
  worker_name
  coin
  account
  ```
  ... for example:
  - "My EMCD username.1023 (BTC) worker" (`sensor.my_emcd_username.1023_btc_worker`)
  - "My EMCD username.1024 (LTC) worker" (`sensor.my_emcd_username.1024_ltc_worker`)

- Rewards sensors for each bundle (account + coin) with attributes...
  ```
  last reward
  previous reward
  coin
  account
  ```
  - "My EMCD username (BTC) rewards" (`sensor.my_emcd_username_btc_rewards`)
  - "My EMCD username (LTC) rewards" (`sensor.my_emcd_username_ltc_rewards`)

- Payouts sensors for each bundle (account + coin) with attributes...
  ```
  last payout
  previous payout
  coin
  account
  ```
  - "My EMCD username (BTC) payouts" (`sensor.my_emcd_username_btc_payouts`)
  - "My EMCD username (LTC) payouts" (`sensor.my_emcd_username_ltc_payouts`)

### Configuration details
---

#### `name`
The `name` you specify will be used as a prefix for all the sensors this integration creates. By default, the prefix is simply "EMCD".

#### `api_key`
An API key from EMCD are **required** for this integration to function.  It is *highly recommended* to store your API key in Home Assistant's `secrets.yaml` file.

#### `coins`
A list of coins, You want to add for monitoring in HomeAssistant. By default? sensors for all coins will be created

## Donate

if You like this component - feel free to donate me

* BTC: 1ALWfyhkniqZjLzckS2GDKmQXvEnzvDfth 
* ETH: 0xef89238d7a30694041e64e31b7991344e618923f
* LTC: LeHu1RaJhjH6bsoiqtEwZoZg6K6qeorsRf
* USDT: TFLt756zrKRFcvhSkjSWaXkfEzhv2M55YN
