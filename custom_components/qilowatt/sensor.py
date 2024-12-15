# custom_components/qilowatt/sensor.py

import logging

from homeassistant.components.sensor import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity
from qilowatt import WorkModeCommand

from .const import CONF_INVERTER_ID, DATA_CLIENT, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up Qilowatt sensors."""
    inverter_id = config_entry.data[CONF_INVERTER_ID]

    # Add sensors for WORKMODE commands
    workmode_sensors = []
    workmode_fields = [
        "Mode",
        "_source",
        "BatterySoc",
        "PowerLimit",
        "PeakShaving",
        "ChargeCurrent",
        "DischargeCurrent",
    ]
    for field in workmode_fields:
        sensor = WorkModeSensor(
            inverter_id,
            field,
            config_entry,
        )
        workmode_sensors.append(sensor)

    async_add_entities(workmode_sensors, update_before_add=True)


class WorkModeSensor(Entity):
    """Sensor for WORKMODE command fields."""

    def __init__(self, inverter_id, field_name, entry) -> None:
        self._inverter_id = inverter_id
        self._field_name = field_name
        self.entry = entry
        self._name = field_name
        self._unique_id = f"{inverter_id}_{field_name}"
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.entry.title,
            manufacturer="Qilowatt",
            model=self.entry.data["inverter_model"],
            via_device=(DOMAIN, self.entry.entry_id),
        )

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_added_to_hass(self):
        """Register dispatcher to listen for WORKMODE updates."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_workmode_update_{self._inverter_id}",
                self._handle_workmode_update,
            )
        )

    async def _handle_workmode_update(self, command: WorkModeCommand):
        """Handle WORKMODE command updates."""
        _LOGGER.debug(f"WorkModeSensor '{self._name}' handling update.")
        value = getattr(command, self._field_name, None)
        self._state = value
        self.async_schedule_update_ha_state()
