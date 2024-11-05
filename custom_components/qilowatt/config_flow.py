import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_INVERTER_ID,
    CONF_INVERTER_MODEL,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_USERNAME,
    DOMAIN,
    SUPPORTED_INVERTERS,
)


class QilowattConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Qilowatt Integration."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return QilowattOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate the input here if needed
            return self.async_create_entry(
                title=f"Inverter {user_input[CONF_INVERTER_ID]}", data=user_input
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_MQTT_USERNAME): str,
                vol.Required(CONF_MQTT_PASSWORD): str,
                vol.Required(CONF_INVERTER_ID): str,
                vol.Required(CONF_INVERTER_MODEL): vol.In(SUPPORTED_INVERTERS),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class QilowattOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Handle options step."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional("update_interval", default=30): vol.All(
                    vol.Coerce(int), vol.Range(min=5)
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
