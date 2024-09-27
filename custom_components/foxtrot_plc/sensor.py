"""Sensor platform for Foxtrot PLC."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    PERCENTAGE,
    POWER_WATT,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FoxtrotPLCCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for Foxtrot PLC."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for variable, value in coordinator.data.items():
        if isinstance(value, (int, float)):
            entities.append(FoxtrotPLCNumericSensor(coordinator, variable))
        elif isinstance(value, str):
            entities.append(FoxtrotPLCStringSensor(coordinator, variable))
    async_add_entities(entities)


class FoxtrotPLCNumericSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Foxtrot PLC numeric sensor."""

    def __init__(
        self, coordinator: FoxtrotPLCCoordinator, variable: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._variable = variable
        self._attr_unique_id = f"{
            coordinator.config_entry.entry_id}_{variable}"
        self._attr_name = f"Foxtrot PLC {variable}"

        # Set state class for long-term statistics
        self._attr_state_class = SensorStateClass.MEASUREMENT

        # Attempt to determine device class and unit of measurement
        if "temp" in variable.lower():
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = TEMP_CELSIUS
        elif "humidity" in variable.lower():
            self._attr_device_class = SensorDeviceClass.HUMIDITY
            self._attr_native_unit_of_measurement = PERCENTAGE
        elif "power" in variable.lower():
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_native_unit_of_measurement = POWER_WATT
        elif "energy" in variable.lower():
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        else:
            # Default to None if we can't determine the type
            self._attr_device_class = None
            self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._variable)
        if isinstance(value, float):
            return round(value, 2)
        return value


class FoxtrotPLCStringSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Foxtrot PLC string sensor."""

    def __init__(
        self, coordinator: FoxtrotPLCCoordinator, variable: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._variable = variable
        self._attr_unique_id = f"{
            coordinator.config_entry.entry_id}_{variable}"
        self._attr_name = f"Foxtrot PLC {variable}"

        # String sensors don't have state class or device class
        self._attr_state_class = None
        self._attr_device_class = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._variable)
