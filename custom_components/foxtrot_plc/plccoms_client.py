import asyncio
import logging
from async_timeout import timeout

_LOGGER = logging.getLogger(__name__)

class PLCComsClient:
    """Client to handle PLCComS protocol with improved async handling."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize the client."""
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self._lock = asyncio.Lock()
        self.connection_timeout = 10  # seconds
        self.command_timeout = 5  # seconds

    async def connect(self) -> None:
        """Connect to the PLC."""
        if self.reader and self.writer:
            return  # Already connected

        try:
            async with timeout(self.connection_timeout):
                self.reader, self.writer = await asyncio.open_connection(
                    self.host, self.port
                )
            _LOGGER.info(f"Connected to PLC at {self.host}:{self.port}")
        except asyncio.TimeoutError:
            _LOGGER.error(f"Connection timeout to PLC at {self.host}:{self.port}")
            raise
        except Exception as e:
            _LOGGER.error(f"Failed to connect to PLC: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from the PLC."""
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception as e:
                _LOGGER.error(f"Error while closing connection: {e}")
        self.reader = None
        self.writer = None
        _LOGGER.info("Disconnected from PLC")

    async def send_command(self, command: str):
        """Send a command to the PLC and return the response."""
        async with self._lock:
            if not self.writer:
                await self.connect()

            try:
                async with timeout(self.command_timeout):
                    self.writer.write(f"{command}\n".encode())
                    await self.writer.drain()
                    response = await self.reader.readuntil(b"\n")
                    return response.decode().strip()
            except asyncio.TimeoutError:
                _LOGGER.error(f"Command timeout: {command}")
                await self.disconnect()  # Disconnect on timeout
                raise
            except Exception as e:
                _LOGGER.error(f"Error sending command '{command}': {e}")
                await self.disconnect()  # Disconnect on error
                raise

    async def list_variables(self):
        """List all variables from the PLC."""
        variables = []
        try:
            await self.send_command("LIST:")
            while True:
                line = await self.reader.readline()
                if line.strip() == b"LIST:":
                    break
                variable = line.decode().strip()
                if variable.startswith("LIST:"):
                    variable = variable[5:]  # Remove "LIST:" prefix
                if variable:  # Only add non-empty lines
                    variable_name = variable.split(",")[0]  # Remove type information
                    variables.append(variable_name)
        except Exception as e:
            _LOGGER.error(f"Error listing variables: {e}")
            raise
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
                    _LOGGER.warning(f"Unexpected response format for variable {variable}: {response}")
            except Exception as e:
                _LOGGER.error(f"Error getting variable {variable}: {e}")
        return results

    async def set_variable(self, variable: str, value: str) -> None:
        """Set a variable in the PLC."""
        await self.send_command(f"SET:{variable},{value}")
