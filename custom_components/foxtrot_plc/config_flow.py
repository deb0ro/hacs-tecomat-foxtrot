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
    DOMAIN,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PLC_IP): str,
        vol.Required(CONF_PLC_PORT, default=5010): int,
        vol.Required(CONF_SCAN_INTERVAL, default=30): int,
        vol.Required(CONF_VARIABLE_PREFIXES): str,
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

        # If options are empty, try to get values from data
        if CONF_SCAN_INTERVAL not in options:
            options[CONF_SCAN_INTERVAL] = self.config_entry.data.get(
                CONF_SCAN_INTERVAL, 30
            )
        if CONF_VARIABLE_PREFIXES not in options:
            options[CONF_VARIABLE_PREFIXES] = self.config_entry.data.get(
                CONF_VARIABLE_PREFIXES, ""
            )

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
                        description="""Enter prefixes separated by commas,
                          e.g. 'TEPLOTY,ZALUZIE'""",
                    ): str,
                    vol.Required(
                        CONF_IGNORE_ZERO,
                        default=options.get(CONF_IGNORE_ZERO, True),
                    ): bool,
                }
            ),
        )
