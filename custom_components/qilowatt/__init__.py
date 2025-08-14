"""Qilowatt integration for Home Assistant."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers.event import async_call_later

from .const import DATA_CLIENT, DOMAIN
from .mqtt_client import MQTTClient

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Qilowatt integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Qilowatt from a config entry with a 60s delay after HA start."""

    async def _delayed_start(_now):
        hass.data.setdefault(DOMAIN, {})
        client = MQTTClient(hass, entry)
        hass.data[DOMAIN][entry.entry_id] = {DATA_CLIENT: client}

        # Start the client asynchronously
        await client.start()

        # Use the new method and await it
        await hass.config_entries.async_forward_entry_setups(
            entry, ["sensor", "binary_sensor"]
        )

        _LOGGER.warning("Qilowatt integration started after 60 seconds delay")

    async def _schedule_start(_event):
        _LOGGER.warning("Qilowatt integration will be started after 60 seconds delay")
        async_call_later(hass, 60, _delayed_start)

    # Ждём запуска всей системы, потом даём 60 секунд задержки
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _schedule_start)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a Qilowatt config entry."""
    client = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]
    await hass.async_add_executor_job(client.stop)
    hass.data[DOMAIN].pop(entry.entry_id)

    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")

    return True
