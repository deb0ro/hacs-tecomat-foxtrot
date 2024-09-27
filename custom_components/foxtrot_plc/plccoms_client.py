import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class PLCComsClient:
    """Client to handle PLCComS protocol."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize the client."""
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self) -> None:
        """Connect to the PLC."""
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port
        )

    async def disconnect(self) -> None:
        """Disconnect from the PLC."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def send_command(self, command: str):
        """Send a command to the PLC and return the response."""
        if not self.writer:
            await self.connect()
        self.writer.write(f"{command}\n".encode())
        await self.writer.drain()
        response = await self.reader.readuntil(b"\n")
        return response.decode().strip()

    async def list_variables(self):
        """List all variables from the PLC."""
        await self.send_command("LIST:")
        variables = []
        while True:
            try:
                line = await asyncio.wait_for(
                    self.reader.readline(), timeout=5.0
                )
                if line.strip() == b"LIST:":
                    break
                variable = line.decode().strip()
                if variable.startswith("LIST:"):
                    variable = variable[5:]  # Remove "LIST:" prefix
                if variable:  # Only add non-empty lines
                    variable_name = variable.split(",")[
                        0
                    ]  # Remove type information
                    variables.append(variable_name)
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout while reading variables list")
                break
            except Exception as e:
                _LOGGER.error(f"Error reading variable: {e}")
                break
        return variables

    async def get_variables(self, variables):
        """Get the values of specified variables."""
        results = {}
        for variable in variables:
            try:
                response = await self.send_command(f"GET:{variable}")
                parts = response.split(",", 1)
                if len(parts) == 2:
                    value = parts[1]
                    results[variable] = value
                else:
                    _LOGGER.warning(
                        f"""Unexpected response format for variable
                          {variable}: {response}"""
                    )
            except Exception as e:
                _LOGGER.error(f"Error getting variable {variable}: {e}")
        return results

    async def set_variable(self, variable: str, value: str) -> None:
        """Set a variable in the PLC."""
        await self.send_command(f"SET:{variable},{value}")
