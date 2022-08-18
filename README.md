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

To use this component, add new integration via HomeAssistant GUI or add the following to your `configuration.yaml` file:

```yaml
emcd_pool:
  - api_key: !secret emcd_api_key
  
```

#### Configuration variables:
| Key               | Type   | Required | Description                               | Default |
| :---------------- | :----: | :------: |:--------------------------------------    | :-----: |
| `api_key`         | string | Yes      | Your's EMCD API key                       | -       |

This configuration will create the following entities in your Home Assistant instance (assume, that api_key's owner's account is "username" for example) :

- Info sensors for each bundle (account + coin) with attributes...
  ```
  balance
  total paid
  min payout
  payout address
  coin
  account
  ```
  - "EMCD username (BTC) info" (`sensor.emcd_username_btc_info`)
  - "EMCD username (LTC) info" (`sensor.emcd_username_ltc_info`)

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
  - "EMCD username (BTC) status" (`sensor.emcd_username_btc_status`)
  - "EMCD username (LTC) status" (`sensor.emcd_username_ltc_status`)  

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
  - "EMCD username.1023 (BTC) worker" (`sensor.emcd_username.1023_btc_worker`)
  - "EMCD username.1024 (LTC) worker" (`sensor.emcd_username.1024_ltc_worker`)

- Rewards sensors for each bundle (account + coin) with attributes...
  ```
  income
  hashrate
  reward type
  unix timestamp
  datetime
  coin
  account
  ```
  - "EMCD username (BTC) rewards" (`sensor.emcd_username_btc_rewards`)
  - "EMCD username (LTC) rewards" (`sensor.emcd_username_ltc_rewards`)

- Payouts sensors for each bundle (account + coin) with attributes...
  ```
  amount
  transaction id
  unix timestamp
  datetime  
  coin
  account
  ```
  - "EMCD username (BTC) payouts" (`sensor.emcd_username_btc_payouts`)
  - "EMCD username (LTC) payouts" (`sensor.emcd_username_ltc_payouts`)

### Configuration details
---

#### `api_key`
An API key from EMCD are **required** for this integration to function.  It is *highly recommended* to store your API key in Home Assistant's `secrets.yaml` file.

## Donate

if You like this component - feel free to donate me

* BTC: 1ALWfyhkniqZjLzckS2GDKmQXvEnzvDfth 
* ETH: 0xef89238d7a30694041e64e31b7991344e618923f
* LTC: LeHu1RaJhjH6bsoiqtEwZoZg6K6qeorsRf
* USDT: TFLt756zrKRFcvhSkjSWaXkfEzhv2M55YN
