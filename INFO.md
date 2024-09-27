# Foxtrot PLC Integration for Home Assistant

![Foxtrot PLC Logo](TODO)

## Overview

The Foxtrot PLC HACS integration allows you to connect your Tecomat Foxtrot PLC to Home Assistant, enabling real-time monitoring and control of PLC variables directly from your smart home dashboard.

## Features

- 🔄 Automatic discovery of PLC variables
- 📊 Support for both numeric and string variables
- 📈 Long-term statistics for numeric sensors
- ⏱️ Configurable scan interval
- 0️⃣ Option to ignore zero or empty values
- 🔢 Decimal precision control (displayed with 2 decimal places)

## Screenshot

![Foxtrot PLC Integration Screenshot](TODO)

## Configuration

During setup, you'll need to provide:

- PLC IP Address
- PLCComS Port (default: 5010)
- Scan Interval
- Variable Prefixes (e.g., "TEPLOTY,ZALUZIE")

## Usage

Once configured, the integration will create sensor entities in Home Assistant for each discovered PLC variable. These can be used in automations, scripts, and dashboards just like any other Home Assistant entity.

## Support

📚 [Full Documentation](https://github.com/deb0ro/hacs-tecomat-foxtrot)
🐛 [Report an Issue](https://github.com/deb0ro/hacs-tecomat-foxtrot/issues)
💡 [Feature Requests](https://github.com/deb0ro/hacs-tecomat-foxtrot/issues)

## About

This integration is community-maintained and not officially associated with Teco a.s. Always ensure you're using the latest version for the best experience and newest features!

---

Enjoying the integration? Consider starring the repository on GitHub! ⭐