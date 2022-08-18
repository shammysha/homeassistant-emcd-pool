import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from typing import (
    Any, 
    Dict, 
    Final, 
    List, 
    Optional
)

from homeassistant.config_entries import (
    ConfigFlow 
)

from homeassistant.const import (
    CONF_API_KEY, 
    CONF_USERNAME
)

from .const import (
    FLOW_VERSION,
    DOMAIN 
)

class EMCDPoolConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION: Final[int] = FLOW_VERSION
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self._save_config: Optional[Dict[str, Any]] = None
        self._save_options: Optional[Dict[str, Any]] = None
        self._entity_config_keys: Optional[List[str]] = None
        
        self.api_data = False
        
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
    
    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        errors = {}
        
        if user_input:
            try:
                api_key = user_input[CONF_API_KEY]
                
            except (TypeError, ValueError, LookupError):
                errors[CONF_API_KEY] = "invalid_credentials"
             
            else:    
                username = await self.async_fetch_username(api_key)
                    
                if username:
                    await self.async_set_unique_id(username)
                    self._abort_if_unique_id_configured()
  
                    return self.async_create_entry(title=username, data={
                        CONF_API_KEY: api_key,
                        CONF_USERNAME: username
                    })                    
                    
                errors[CONF_API_KEY] = "invalid_credentials"

        else:
            user_input = {}
    
        return self.async_show_form( 
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY, default=user_input.get(CONF_API_KEY, None)): cv.string   
            }),
            errors=errors
        )
            
    async def async_step_import(self, user_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not user_input:
            return self.async_abort(reason="empty_config")
        
        if not user_input[CONF_API_KEY]:
            return self.async_abort(reason="invalid_credentials")            
            
        user_input[CONF_USERNAME] = await self.async_fetch_username(user_input[CONF_API_KEY])
        
        if user_input[CONF_USERNAME]:
            await self.async_set_unique_id(user_input[CONF_USERNAME])
            self._abort_if_unique_id_configured()   
            
            return self.async_create_entry(title=user_input[CONF_USERNAME], data=user_input)
        
        return self.async_abort(reason="invalid_credentials")
