import asyncio
import inspect
import json
import logging
import os
from typing import Dict, Final, Mapping, Optional, TYPE_CHECKING, Tuple, Type

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.const import CONF_USERNAME
from .const import DOMAIN
from emcd_pool.exceptions import EMCDAPIException

@callback
async def find_existing_entry(hass: HomeAssistantType, api_key: str, username: str = None) -> Optional[ConfigEntry]:
    if not username:
        username = await async_fetch_username(api_key)

    if not username:
        raise EMCDAPIException('Invalid credentials')

    existing_entries = hass.config_entries.async_entries(DOMAIN)
    for config_entry in existing_entries:
        if config_entry.data[CONF_USERNAME] == username:
            return config_entry
        
async def async_fetch_username(self, api_key):
    username = None
    
    from .client import EMCDPoolClient
    client = EMCDPoolClient(api_key)
                
    try:
        info = await client.async_get_info()
    except Exception as e:
        await client.close_connection()
        raise e
            
    else:
        username = info.pop('username', None)
                
    finally:
        await client.close_connection()        
    
    return username 
        
