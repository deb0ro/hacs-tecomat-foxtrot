"""Config flow for Foxtrot PLC integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

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
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PLC_IP): str,
        vol.Required(CONF_PLC_PORT, default=5010): int,
        vol.Required(CONF_SCAN_INTERVAL, default=30): int,
        vol.Required(CONF_VARIABLE_PREFIXES): str,
        vol.Optional(CONF_EXCLUDE_VARIABLE_PREFIXES, default=""): str,
        vol.Required(CONF_LOG_LEVEL, default=LOG_LEVEL_INFO): vol.In([
            LOG_LEVEL_DEBUG,
            LOG_LEVEL_INFO,
            LOG_LEVEL_WARNING,
            LOG_LEVEL_ERROR,
        ]),
        vol.Required(CONF_DETAILED_LOGGING, default=False): bool,
    }
)

class FoxtrotPLCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Foxtrot PLC."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Separate the data into config_entry data and options
            data = {
                CONF_PLC_IP: user_input[CONF_PLC_IP],
                CONF_PLC_PORT: user_input[CONF_PLC_PORT],
            }
            options = {
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                CONF_VARIABLE_PREFIXES: user_input[CONF_VARIABLE_PREFIXES],
                CONF_EXCLUDE_VARIABLE_PREFIXES: user_input[CONF_EXCLUDE_VARIABLE_PREFIXES],
                CONF_LOG_LEVEL: user_input[CONF_LOG_LEVEL],
                CONF_DETAILED_LOGGING: user_input[CONF_DETAILED_LOGGING],
            }

            return self.async_create_entry(
                title=f"Foxtrot PLC ({user_input[CONF_PLC_IP]})",
                data=data,
                options=options,
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Foxtrot PLC integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = dict(self.config_entry.options)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=options.get(CONF_SCAN_INTERVAL, 30),
                    ): int,
                    vol.Required(
                        CONF_VARIABLE_PREFIXES,
                        default=options.get(CONF_VARIABLE_PREFIXES, ""),
                    ): str,
                    vol.Optional(
                        CONF_EXCLUDE_VARIABLE_PREFIXES,
                        default=options.get(CONF_EXCLUDE_VARIABLE_PREFIXES, ""),
                    ): str,
                    vol.Required(
                        CONF_IGNORE_ZERO,
                        default=options.get(CONF_IGNORE_ZERO, True),
                    ): bool,
                    vol.Required(
                        CONF_LOG_LEVEL,
                        default=options.get(CONF_LOG_LEVEL, LOG_LEVEL_INFO),
                    ): vol.In([
                        LOG_LEVEL_DEBUG,
                        LOG_LEVEL_INFO,
                        LOG_LEVEL_WARNING,
                        LOG_LEVEL_ERROR,
                    ]),
                    vol.Required(
                        CONF_DETAILED_LOGGING,
                        default=options.get(CONF_DETAILED_LOGGING, False),
                    ): bool,
                }
            ),
        )