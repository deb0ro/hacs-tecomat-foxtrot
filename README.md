# Foxtrot PLC Integration for Home Assistant

## Overview

The Foxtrot PLC HACS integration allows you to connect your Tecomat Foxtrot PLC to Home Assistant, enabling you to monitor and control various PLC variables directly from your Home Assistant instance.

## Features

- Automatic discovery of PLC variables based on specified prefixes
- Support for both numeric and string variables
- Long-term statistics for numeric sensors
- Configurable scan interval
- Option to ignore zero or empty values
- Decimal precision control for numeric values (displayed with 2 decimal places)

## Installation

1. Copy the `foxtrot_plc` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to Configuration > Integrations.
4. Click on the "+ ADD INTEGRATION" button and search for "Foxtrot PLC".
5. Follow the configuration steps.

## Configuration

During the setup, you'll need to provide the following information:

- **PLC IP Address**: The IP address of your Foxtrot PLC.
- **PLCComS Port**: The port number for PLCComS communication (default is 5010).
- **Scan Interval**: How often (in seconds) the integration should fetch data from the PLC.
- **Variable Prefixes**: A comma-separated list of prefixes to filter which variables to import (e.g., "TEPLOTY,ZALUZIE").

## Options

After initial setup, you can modify the following options:

1. Go to Configuration > Integrations.
2. Find the Foxtrot PLC integration and click on "CONFIGURE".
3. You can adjust:
   - **Scan Interval**: Change how often data is fetched from the PLC.
   - **Variable Prefixes**: Modify which variables are being monitored.
   - **Ignore Zero Values**: Toggle whether to ignore variables with zero or empty values.

## Usage

Once configured, the integration will create sensor entities in Home Assistant for each discovered PLC variable. These entities will be named according to the variable names in your PLC.

- Numeric variables will be represented as sensors with long-term statistics enabled.
- String variables will be represented as text sensors.

## Troubleshooting

- If you're not seeing expected variables, check your "Variable Prefixes" setting and ensure it matches the naming convention in your PLC.
- For issues with connection, verify the PLC IP address and port number.
- Check Home Assistant logs for any error messages related to the Foxtrot PLC integration.

## Support

For bugs, feature requests, or questions, please open an issue on the GitHub repository.

## Disclaimer

This integration is not officially associated with Teco a.s. Use at your own risk.

## License

[MIT License](LICENSE)