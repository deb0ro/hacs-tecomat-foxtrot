"""Sensor platform for Foxtrot PLC."""
import logging

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FoxtrotPLCCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for Foxtrot PLC."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for variable, value in coordinator.data.items():
        _LOGGER.debug(f"Creating entity for variable: {variable} with value: {value}")
        entities.append(FoxtrotPLCSensor(coordinator, variable))
    _LOGGER.info(f"Adding {len(entities)} entities to Home Assistant")
    async_add_entities(entities)

class FoxtrotPLCSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Foxtrot PLC sensor."""

    def __init__(
        self, coordinator: FoxtrotPLCCoordinator, variable: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._variable = variable
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{variable}"
        self._attr_name = f"Foxtrot PLC {variable}"

        # Set default values
        self._attr_state_class = None
        self._attr_device_class = None
        self._attr_native_unit_of_measurement = None
        self._is_temperature = False

        # Determine sensor type and unit based on variable name
        lower_var = variable.lower()
        if "temp" in lower_var or "teploty" in lower_var:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._is_temperature = True
            if self._is_numeric(coordinator.data.get(variable)):
                self._attr_state_class = SensorStateClass.MEASUREMENT
        elif "humidity" in lower_var or "vlhkost" in lower_var:
            if self._is_numeric(coordinator.data.get(variable)):
                self._attr_device_class = SensorDeviceClass.HUMIDITY
                self._attr_native_unit_of_measurement = PERCENTAGE
                self._attr_state_class = SensorStateClass.MEASUREMENT
        elif "power" in lower_var or "vykon" in lower_var:
            if self._is_numeric(coordinator.data.get(variable)):
                self._attr_device_class = SensorDeviceClass.POWER
                self._attr_native_unit_of_measurement = UnitOfPower.WATT
                self._attr_state_class = SensorStateClass.MEASUREMENT
        elif "energy" in lower_var or "energie" in lower_var:
            if self._is_numeric(coordinator.data.get(variable)):
                self._attr_device_class = SensorDeviceClass.ENERGY
                self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @staticmethod
    def _is_numeric(value: Any) -> bool:
        """Check if the value is numeric."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._variable)
        if self._is_numeric(value):
            return round(float(value), 2)
        return value

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the state class of the sensor."""
        if self._is_numeric(self.coordinator.data.get(self._variable)):
            return self._attr_state_class
        return None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        if self._is_temperature:
            return UnitOfTemperature.CELSIUS
        return self._attr_native_unit_of_measurement if self._is_numeric(self.coordinator.data.get(self._variable)) else None