"""DataUpdateCoordinator for Foxtrot PLC."""

import logging
import re
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .plccoms_client import PLCComsClient

_LOGGER = logging.getLogger(__name__)


class FoxtrotPLCCoordinator(DataUpdateCoordinator):
    """Coordinator for Foxtrot PLC."""

    def __init__(
        self,
        hass: HomeAssistant,
        plc_ip: str,
        plc_port: int,
        variable_prefixes: str,
        scan_interval: int,
        ignore_zero: bool,
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
            prefix.strip() for prefix in variable_prefixes.split(",")
        ]
        self.ignore_zero = ignore_zero

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            variables = await self.client.list_variables()
            _LOGGER.debug(f"Retrieved variables: {variables}")
            if not variables:
                _LOGGER.warning("No variables returned from PLC")
                return {}
            filtered_variables = self._filter_variables(variables)
            _LOGGER.debug(f"Filtered variables: {filtered_variables}")
            if not filtered_variables:
                _LOGGER.warning(
                    f"No variables match the filters: {self.variable_prefixes}"
                )
                return {}
            data = await self.client.get_variables(filtered_variables)
            _LOGGER.debug(f"Retrieved data: {data}")

            # Parse the values
            parsed_data = {}
            for var, value in data.items():
                parsed_value = self._parse_value(value)
                if not self.ignore_zero or not self._is_zero_or_empty(
                    parsed_value
                ):
                    parsed_data[var] = parsed_value

            return parsed_data
        except Exception as err:
            _LOGGER.error(f"Error communicating with PLC: {err}")
            raise UpdateFailed(f"Error communicating with PLC: {err}") from err

    def _filter_variables(self, variables):
        """Filter variables based on the prefixes."""
        if not self.variable_prefixes:
            return variables

        filtered = []
        for prefix in self.variable_prefixes:
            # Create a case-insensitive regular expression
            regex = re.compile(re.escape(prefix), re.IGNORECASE)
            filtered.extend([v for v in variables if regex.search(v)])

        return list(set(filtered))  # Remove duplicates

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
