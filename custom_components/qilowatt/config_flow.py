import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_DEVICE_ID,
    CONF_INVERTER_ID,
    CONF_INVERTER_MODEL,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_USERNAME,
    CONF_BATTERY_SOC_SENSOR,
    DOMAIN,
)


class QilowattConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Qilowatt Integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        available_inverters = await self._discover_inverters()
        if user_input is not None:
            # Validate the input here if needed
            selected_device_id = user_input["device_id"]
            user_input[CONF_INVERTER_MODEL] = available_inverters[selected_device_id]["inverter_integration"]
            return self.async_create_entry(
                title=f"{available_inverters[selected_device_id]['name']}",
                data=user_input,
            )

        inverter_options = {
            device_id: inverter["name"]
            for device_id, inverter in available_inverters.items()
        }

        # Define the base schema without the battery_soc_sensor
        base_schema = {
            vol.Required(CONF_MQTT_USERNAME): str,
            vol.Required(CONF_MQTT_PASSWORD): str,
            vol.Required(CONF_INVERTER_ID): str,
            vol.Required(CONF_DEVICE_ID): vol.In(inverter_options),
        }

        # Add the battery_soc_sensor field conditionally if Sofar inverter is selected
        if user_input and user_input.get(CONF_DEVICE_ID) in available_inverters:
            selected_inverter = available_inverters[user_input[CONF_DEVICE_ID]]
            if selected_inverter["inverter_integration"] == "Sofar":
                base_schema[vol.Optional(CONF_BATTERY_SOC_SENSOR)] = str

        data_schema = vol.Schema(base_schema)

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _discover_inverters(self):
        """Discover inverters in Home Assistant."""
        device_registry = dr.async_get(self.hass)
        inverters = {}

        for device in device_registry.devices.values():
            for identifier in device.identifiers:
                domain, device_id, *_ = identifier
                if domain == "mqtt":
                    # Solar Assistant inverter
                    if "sa_inverter" in device_id:
                        inverters[device.id] = {
                            "name": device.name,
                            "inverter_integration": "SolarAssistant",
                        }
                if domain == "solarman":
                    # Solarman inverter integration
                    inverters[device.id] = {
                        "name": device.name,
                        "inverter_integration": "Solarman",
                    }
                if domain == "solax_modbus":
                    # Sofar Modbus inverter integration
                    inverters[device.id] = {
                        "name": device.name,
                        "inverter_integration": "Sofar",
                    }
        return inverters