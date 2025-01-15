import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from qilowatt import EnergyData, MetricsData

from .base_inverter import BaseInverter
from ..const import CONF_BATTERY_SOC_SENSOR

_LOGGER = logging.getLogger(__name__)


class SofarInverter(BaseInverter):
    """Implementation for Sofar integrated inverters."""

    def __init__(self, hass: HomeAssistant, config_entry):
        super().__init__(hass, config_entry)
        self.hass = hass
        self.device_id = config_entry.data["device_id"]
        self.battery_soc_sensor = config_entry.data.get(CONF_BATTERY_SOC_SENSOR)
        self.entity_registry = er.async_get(hass)
        self.inverter_entities = {}
        for entity in self.entity_registry.entities.values():
            if entity.device_id == self.device_id:
                self.inverter_entities[entity.entity_id] = entity.name

    def find_entity_state(self, entity_id):
        """Helper method to find a state by entity_id (for Sofar sensors)."""
        return next(
            (
                self.hass.states.get(entity)
                for entity in self.inverter_entities
                if entity.endswith(entity_id)
            ),
            None,
        )

    def get_state_float(self, entity_id, default=0.0):
        """Helper method to get a sensor state as float (for Sofar sensors)."""
        state = self.find_entity_state(entity_id)
        if state and state.state not in ("unknown", "unavailable", ""):
            try:
                return float(state.state)
            except ValueError:
                _LOGGER.warning(f"Could not convert state of {entity_id} to float")
        else:
            _LOGGER.warning(f"State of {entity_id} is unavailable or unknown")
        return default

    def get_state_int(self, entity_id, default=0):
        """Helper method to get a sensor state as int (for Sofar sensors)."""
        state = self.find_entity_state(entity_id)
        if state and state.state not in ("unknown", "unavailable", ""):
            try:
                return int(float(state.state))
            except ValueError:
                _LOGGER.warning(f"Could not convert state of {entity_id} to int")
        else:
            _LOGGER.warning(f"State of {entity_id} is unavailable or unknown")
        return default

    def get_state_text(self, entity_id, default=""):
        """Helper method to get a sensor state as text (for Sofar sensors)."""
        state = self.find_entity_state(entity_id)
        if state and state.state not in ("unknown", "unavailable", "", None):
            return str(state.state)
        else:
            _LOGGER.warning(f"State of {entity_id} is unavailable, unknown, or empty")
        return default

    def find_external_entity_state(self, entity_id):
        """Helper method to find a state for external sensors by entity_id."""
        return self.hass.states.get(entity_id)

    def get_external_state_float(self, entity_id, default=0.0):
        """Helper method to get an external sensor state as float."""
        state = self.find_external_entity_state(entity_id)
        if state and state.state not in ("unknown", "unavailable", ""):
            try:
                return float(state.state)
            except ValueError:
                _LOGGER.warning(f"Could not convert state of {entity_id} to float")
        else:
            _LOGGER.warning(f"State of {entity_id} is unavailable or unknown")
        return default

    def get_external_state_int(self, entity_id, default=0):
        """Helper method to get an external sensor state as int."""
        state = self.find_external_entity_state(entity_id)
        if state and state.state not in ("unknown", "unavailable", ""):
            try:
                return int(float(state.state))
            except ValueError:
                _LOGGER.warning(f"Could not convert state of {entity_id} to int")
        else:
            _LOGGER.warning(f"State of {entity_id} is unavailable or unknown")
        return default

    def get_external_state_text(self, entity_id, default=""):
        """Helper method to get an external sensor state as text (string)."""
        state = self.find_external_entity_state(entity_id)
        if state and state.state not in ("unknown", "unavailable", "", None):
            return str(state.state)
        else:
            _LOGGER.warning(f"State of {entity_id} is unavailable, unknown, or empty")
        return default

    # Rest of your methods (get_energy_data, get_metrics_data, etc.) remain unchanged

    def get_energy_data(self):
        """Retrieve ENERGY data."""
        # Sensor is in kW and swap positive with negative and vice versa
        power = [
            self.get_state_float("sofar_active_power_pcc_l1") * -1000,
            self.get_state_float("sofar_active_power_pcc_l2") * -1000,
            self.get_state_float("sofar_active_power_pcc_l3") * -1000,
        ]
        today = self.get_state_float("sofar_import_energy_today")
        total = 0.0  # As per payload
        current = [
            self.get_state_float("sofar_current_pcc_l1"),
            self.get_state_float("sofar_current_pcc_l2"),
            self.get_state_float("sofar_current_pcc_l3"),
        ]

        # Define voltage as self, because we need it in another function to calculate current from power
        self.voltage = [
            self.get_state_float("sofar_voltage_l1"),
            self.get_state_float("sofar_voltage_l2"),
            self.get_state_float("sofar_voltage_l3"),
        ]
        frequency = self.get_state_float("sofar_grid_frequency")

        return EnergyData(
            Power=power,
            Today=today,
            Total=total,
            Current=current,
            Voltage=self.voltage,
            Frequency=frequency,
        )

    def get_metrics_data(self):
        """Retrieve METRICS data."""
        pv_power = [
            self.get_state_float("sofar_pv_power_1") * 1000,
            self.get_state_float("sofar_pv_power_2") * 1000,
        ]
        pv_voltage = [
            self.get_state_float("sofar_pv_voltage_1"),
            self.get_state_float("sofar_pv_voltage_2"),
        ]
        pv_current = [
            self.get_state_float("sofar_pv_current_1"),
            self.get_state_float("sofar_pv_current_2"),
        ]
        #load_power = self.get_state_float("sofar_active_power_load_sys") * 1000

        # Create power array values from one sensor
        combined_power = self.get_state_float("sofar_active_power_load_sys") * 1000
        load_power = [combined_power / 3] * 3
        load_power = [round(x) for x in load_power]

        alarm_codes = [
            self.get_state_text("sofar_fault_1"),
            self.get_state_text("sofar_fault_2"),
            self.get_state_text("sofar_fault_3"),
            self.get_state_text("sofar_fault_4"),
            self.get_state_text("sofar_fault_5"),
            self.get_state_text("sofar_fault_6"),
        ]

        # Use custom battery_soc_sensor if provided, otherwise use the default
        if self.battery_soc_sensor:
            battery_soc = round(self.get_external_state_float(self.battery_soc_sensor) * 100)
        else:
            battery_soc = self.get_state_int("sofar_battery_capacity_total")

        # Calculate current from power and voltage
        load_current = [round(x / y, 2) for x, y in zip(load_power, self.voltage)]  
        #load_current = [0, 0, 0]

        battery_power = [self.get_state_float("sofar_battery_power_total") * 1000]
        battery_current = [self.get_state_float("sofar_battery_current_1")]
        battery_voltage = [self.get_state_float("sofar_battery_voltage_1")]
        inverter_status = 2  # As per payload
        grid_export_limit = 15000
        battery_temperature = [self.get_state_float("sofar_battery_temperature_1")]
        inverter_temperature = self.get_state_float("sofar_inverter_temperature_1")

        return MetricsData(
            PvPower=pv_power,
            PvVoltage=pv_voltage,
            PvCurrent=pv_current,
            LoadPower=load_power,
            AlarmCodes=alarm_codes,
            BatterySOC=battery_soc,
            LoadCurrent=load_current,
            BatteryPower=battery_power,
            BatteryCurrent=battery_current,
            BatteryVoltage=battery_voltage,
            InverterStatus=inverter_status,
            GridExportLimit=grid_export_limit,
            BatteryTemperature=battery_temperature,
            InverterTemperature=inverter_temperature,
        )
