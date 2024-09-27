"""Binary sensor platform for Foxtrot PLC."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
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
    """Set up binary sensors for Foxtrot PLC."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for variable, value in coordinator.data.items():
        if isinstance(
            value, bool
        ):  # Assume boolean values are for binary sensors
            entities.append(FoxtrotPLCBinarySensor(coordinator, variable))
    async_add_entities(entities)


class FoxtrotPLCBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Foxtrot PLC binary sensor."""

    def __init__(
        self, coordinator: FoxtrotPLCCoordinator, variable: str
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._variable = variable
        self._attr_unique_id = f"{
            coordinator.config_entry.entry_id}_{variable}"
        self._attr_name = f"Foxtrot PLC {variable}"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get(self._variable)
