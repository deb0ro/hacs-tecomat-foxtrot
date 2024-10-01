"""The Foxtrot PLC integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_IGNORE_ZERO,
    CONF_PLC_IP,
    CONF_PLC_PORT,
    CONF_SCAN_INTERVAL,
    CONF_VARIABLE_PREFIXES,
    CONF_EXCLUDE_VARIABLE_PREFIXES,
    CONF_LOG_LEVEL,
    CONF_DETAILED_LOGGING,
    DOMAIN,
)
from .coordinator import FoxtrotPLCCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Foxtrot PLC from a config entry."""
    plc_ip = entry.data[CONF_PLC_IP]
    plc_port = entry.data[CONF_PLC_PORT]

    options = dict(entry.options)
    options.setdefault(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, 30))
    options.setdefault(CONF_VARIABLE_PREFIXES, entry.data.get(CONF_VARIABLE_PREFIXES, ""))
    options.setdefault(CONF_EXCLUDE_VARIABLE_PREFIXES, entry.data.get(CONF_EXCLUDE_VARIABLE_PREFIXES, ""))
    options.setdefault(CONF_IGNORE_ZERO, True)
    options.setdefault(CONF_LOG_LEVEL, entry.data.get(CONF_LOG_LEVEL, "info"))
    options.setdefault(CONF_DETAILED_LOGGING, entry.data.get(CONF_DETAILED_LOGGING, False))

    coordinator = FoxtrotPLCCoordinator(
        hass,
        plc_ip,
        plc_port,
        options[CONF_VARIABLE_PREFIXES],
        options[CONF_EXCLUDE_VARIABLE_PREFIXES],
        options[CONF_SCAN_INTERVAL],
        options[CONF_IGNORE_ZERO],
        options[CONF_LOG_LEVEL],
        options[CONF_DETAILED_LOGGING],
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        await coordinator.client.disconnect()
        raise

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    async def async_get_diagnostics(call: ServiceCall) -> None:
        """Handle get diagnostics service call."""
        coordinator = hass.data[DOMAIN][entry.entry_id]
        diagnostics = await coordinator.get_diagnostics()
        hass.components.persistent_notification.async_create(
            f"Foxtrot PLC Diagnostics:\n\n{diagnostics}",
            title="Foxtrot PLC Diagnostics",
        )

    hass.services.async_register(
        DOMAIN,
        "get_diagnostics",
        async_get_diagnostics,
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
