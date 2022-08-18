from typing import Final

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from homeassistant.const import (
    CONF_API_KEY, 
    CONF_USERNAME
)
 
from .const import (
    DOMAIN, 
)

CONFIG_ENTRY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_USERNAME): cv.string
    },
    extra=vol.PREVENT_EXTRA
) 

CONFIG_SCHEMA: Final = vol.Schema(
    {
        vol.Optional(DOMAIN): vol.Any(
            vol.Equal({}),
            vol.Equal(CONFIG_ENTRY_SCHEMA),
            vol.All(
                cv.ensure_list,
                [CONFIG_ENTRY_SCHEMA],
            ),
        )
    },
    extra=vol.ALLOW_EXTRA
)
