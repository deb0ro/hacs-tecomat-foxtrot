import logging
import re
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .plccoms_client import PLCComsClient
from .const import (
    CONF_LOG_LEVEL,
    CONF_DETAILED_LOGGING,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR,
)

_LOGGER = logging.getLogger(__name__)

class FoxtrotPLCCoordinator(DataUpdateCoordinator):
    """Coordinator for Foxtrot PLC."""

    def __init__(
        self,
        hass: HomeAssistant,
        plc_ip: str,
        plc_port: int,
        variable_prefixes: str,
        exclude_variable_prefixes: str,
        scan_interval: int,
        ignore_zero: bool,
        log_level: str,
        detailed_logging: bool,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Foxtrot PLC",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = PLCComsClient(plc_ip, plc_port)
        self.variable_prefixes = [
            prefix.strip() for prefix in variable_prefixes.split(",") if prefix.strip()
        ]
        self.exclude_variable_prefixes = [
            prefix.strip() for prefix in exclude_variable_prefixes.split(",") if prefix.strip()
        ]
        self.ignore_zero = ignore_zero
        self.detailed_logging = detailed_logging
        self._set_log_level(log_level)

    def _set_log_level(self, log_level: str) -> None:
        """Set the log level based on the configuration."""
        if log_level == LOG_LEVEL_DEBUG:
            _LOGGER.setLevel(logging.DEBUG)
        elif log_level == LOG_LEVEL_INFO:
            _LOGGER.setLevel(logging.INFO)
        elif log_level == LOG_LEVEL_WARNING:
            _LOGGER.setLevel(logging.WARNING)
        elif log_level == LOG_LEVEL_ERROR:
            _LOGGER.setLevel(logging.ERROR)

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            variables = await self.client.list_variables()
            if self.detailed_logging:
                _LOGGER.debug(f"Retrieved variables: {variables}")
            else:
                _LOGGER.debug(f"Retrieved {len(variables)} variables")
            
            filtered_variables = self._filter_variables(variables)
            if self.detailed_logging:
                _LOGGER.debug(f"Filtered variables: {filtered_variables}")
            else:
                _LOGGER.debug(f"Filtered to {len(filtered_variables)} variables")
            
            if not filtered_variables:
                _LOGGER.warning(f"No variables match the filters: include={self.variable_prefixes}, exclude={self.exclude_variable_prefixes}")
                return {}
            
            data = await self.client.get_variables(filtered_variables)
            if self.detailed_logging:
                _LOGGER.debug(f"Retrieved data: {data}")
            else:
                _LOGGER.debug(f"Retrieved data for {len(data)} variables")

            # Parse the values
            parsed_data = {}
            for var, value in data.items():
                parsed_value = self._parse_value(value)
                if not self.ignore_zero or not self._is_zero_or_empty(parsed_value):
                    parsed_data[var] = parsed_value
                    if self.detailed_logging:
                        _LOGGER.debug(f"Parsed variable: {var} = {parsed_value}")
                else:
                    if self.detailed_logging:
                        _LOGGER.debug(f"Ignored zero/empty variable: {var} = {parsed_value}")

            _LOGGER.info(f"Update completed, {len(parsed_data)} variables processed")
            return parsed_data
        except Exception as err:
            _LOGGER.error(f"Error communicating with PLC: {err}")
            raise UpdateFailed(f"Error communicating with PLC: {err}") from err

    def _filter_variables(self, variables):
        """Filter variables based on the prefixes and exclude prefixes."""
        if not self.variable_prefixes and not self.exclude_variable_prefixes:
            return variables

        filtered = []
        for variable in variables:
            # Check if the variable should be excluded
            if any(re.search(re.escape(prefix), variable, re.IGNORECASE) for prefix in self.exclude_variable_prefixes):
                _LOGGER.debug(f"Variable {variable} excluded based on exclude prefixes")
                continue
            
            # If include prefixes are specified, check if the variable matches any
            if self.variable_prefixes:
                if any(re.search(re.escape(prefix), variable, re.IGNORECASE) for prefix in self.variable_prefixes):
                    filtered.append(variable)
                    _LOGGER.debug(f"Variable {variable} included based on include prefixes")
            else:
                # If no include prefixes are specified, include all non-excluded variables
                filtered.append(variable)
                _LOGGER.debug(f"Variable {variable} included (no include prefixes specified)")

        return filtered

    def _parse_data(self, data):
        """Parse the values into appropriate types."""
        parsed_data = {}
        for var, value in data.items():
            parsed_value = self._parse_value(value)
            if not self.ignore_zero or not self._is_zero_or_empty(parsed_value):
                parsed_data[var] = parsed_value
        return parsed_data

    def _parse_value(self, value):
        """Parse the value into the appropriate type."""
        try:
            if value.lower() in ["true", "false"]:
                return value.lower() == "true"
            elif "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value  # Keep as string if can't parse

    def _is_zero_or_empty(self, value):
        """Check if a value is zero or empty."""
        if isinstance(value, (int, float)):
            return value == 0 or value == 0.0
        elif isinstance(value, str):
            return value.strip() == "" or value == "0" or value == "0.000000"
        else:
            return False

    async def get_diagnostics(self):
        """Get diagnostic information from the PLC."""
        try:
            _LOGGER.debug("Fetching diagnostic information")
            plc_info = await self.client.send_command("GETINFO:")
            info_lines = plc_info.split("\n")
            diagnostics = {}
            
            for line in info_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "VERSION_PLC":
                        diagnostics[DIAGNOSTIC_PLC_VERSION] = value
                    elif key == "VERSION":
                        diagnostics[DIAGNOSTIC_SERVER_VERSION] = value
                    elif key == "VERSION_EPSNET":
                        diagnostics[DIAGNOSTIC_EPSNET_VERSION] = value
                    elif key == "NETWORK":
                        if DIAGNOSTIC_CONNECTED_CLIENTS not in diagnostics:
                            diagnostics[DIAGNOSTIC_CONNECTED_CLIENTS] = []
                        diagnostics[DIAGNOSTIC_CONNECTED_CLIENTS].append(value)

            active_vars = await self.client.send_command("EN:")
            diagnostics[DIAGNOSTIC_ACTIVE_VARIABLES] = active_vars.split(":")[1].strip()

            _LOGGER.info("Diagnostic information retrieved successfully")
            return diagnostics
        except Exception as err:
            _LOGGER.error(f"Error retrieving diagnostic information: {err}")
            raise