"""The Foxtrot PLC integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_IGNORE_ZERO,
    CONF_PLC_IP,
    CONF_PLC_PORT,
    CONF_SCAN_INTERVAL,
    CONF_VARIABLE_PREFIXES,
    DOMAIN,
)
from .coordinator import FoxtrotPLCCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Foxtrot PLC from a config entry."""
    plc_ip = entry.data[CONF_PLC_IP]
    plc_port = entry.data[CONF_PLC_PORT]

    # Ensure that scan_interval and variable_prefixes are in options
    if (
        CONF_SCAN_INTERVAL not in entry.options
        or CONF_VARIABLE_PREFIXES not in entry.options
        or CONF_IGNORE_ZERO not in entry.options
    ):
        options = dict(entry.options)
        options.setdefault(
            CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, 30)
        )
        options.setdefault(
            CONF_VARIABLE_PREFIXES, entry.data.get(CONF_VARIABLE_PREFIXES, "")
        )
        options.setdefault(CONF_IGNORE_ZERO, True)
        hass.config_entries.async_update_entry(entry, options=options)

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, 30)
    variable_prefixes = entry.options.get(CONF_VARIABLE_PREFIXES, "")
    ignore_zero = entry.options.get(CONF_IGNORE_ZERO, True)

    coordinator = FoxtrotPLCCoordinator(
        hass,
        plc_ip,
        plc_port,
        variable_prefixes,
        scan_interval,
        ignore_zero,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
