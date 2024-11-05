import logging

from homeassistant.core import HomeAssistant
from qilowatt import EnergyData, MetricsData

from .base_inverter import BaseInverter

_LOGGER = logging.getLogger(__name__)


class DeyeSolarAssistantInverter(BaseInverter):
    """Implementation for Deye-SolarAssistant inverter."""

    def __init__(self, hass: HomeAssistant, config_entry):
        super().__init__(hass, config_entry)
        self.hass = hass

    def get_state_float(self, entity_id, default=0.0):
        """Helper method to get a sensor state as float."""
        state = self.hass.states.get(entity_id)
        if state and state.state not in ("unknown", "unavailable", ""):
            try:
                return float(state.state)
            except ValueError:
                _LOGGER.warning(f"Could not convert state of {entity_id} to float")
        else:
            _LOGGER.warning(f"State of {entity_id} is unavailable or unknown")
        return default

    def get_state_int(self, entity_id, default=0):
        """Helper method to get a sensor state as int."""
        state = self.hass.states.get(entity_id)
        if state and state.state not in ("unknown", "unavailable", ""):
            try:
                return int(float(state.state))
            except ValueError:
                _LOGGER.warning(f"Could not convert state of {entity_id} to int")
        else:
            _LOGGER.warning(f"State of {entity_id} is unavailable or unknown")
        return default

    def get_energy_data(self):
        """Retrieve ENERGY data."""
        power = [
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_grid_power_1"),
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_grid_power_2"),
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_grid_power_3"),
        ]
        today = self.get_state_float(
            "sensor.deye_sunsynk_sol_ark_3_phase_grid_energy_in"
        )
        total = 0.0  # As per payload
        current = [0.0, 0.0, 0.0]  # As per payload
        voltage = [
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_grid_voltage_1"),
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_grid_voltage_2"),
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_grid_voltage_3"),
        ]
        frequency = self.get_state_float(
            "sensor.deye_sunsynk_sol_ark_3_phase_grid_frequency"
        )

        return EnergyData(
            Power=power,
            Today=today,
            Total=total,
            Current=current,
            Voltage=voltage,
            Frequency=frequency,
        )

    def get_metrics_data(self):
        """Retrieve METRICS data."""
        pv_power = [
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_pv_power_1"),
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_pv_power_2"),
        ]
        pv_voltage = [
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_pv_voltage_1"),
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_pv_voltage_2"),
        ]
        pv_current = [
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_pv_current_1"),
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_pv_current_2"),
        ]
        load_power = [
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_load_power_1"),
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_load_power_2"),
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_load_power_3"),
        ]
        alarm_codes = [0, 0, 0, 0, 0, 0]  # As per payload
        battery_soc = self.get_state_int(
            "sensor.deye_sunsynk_sol_ark_3_phase_battery_state_of_charge"
        )
        load_current = [0.0, 0.0, 0.0]  # As per payload
        battery_power = [
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_battery_power")
        ]
        battery_current = [
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_battery_current")
        ]
        battery_voltage = [
            self.get_state_float("sensor.deye_sunsynk_sol_ark_3_phase_battery_voltage")
        ]
        inverter_status = 2  # As per payload
        grid_export_limit = self.get_state_float(
            "number.deye_sunsynk_sol_ark_3_phase_max_sell_power"
        )
        battery_temperature = [
            self.get_state_float(
                "sensor.deye_sunsynk_sol_ark_3_phase_battery_temperature"
            )
        ]
        inverter_temperature = self.get_state_float(
            "sensor.deye_sunsynk_sol_ark_3_phase_temperature"
        )

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
