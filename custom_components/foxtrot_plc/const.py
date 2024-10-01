"""Constants for the Foxtrot PLC integration."""

DOMAIN = "foxtrot_plc"
CONF_PLC_IP = "plc_ip"
CONF_PLC_PORT = "plc_port"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_VARIABLE_PREFIXES = "variable_prefixes"
CONF_EXCLUDE_VARIABLE_PREFIXES = "exclude_variable_prefixes"
CONF_IGNORE_ZERO = "ignore_zero_values"
CONF_LOG_LEVEL = "log_level"
CONF_DETAILED_LOGGING = "detailed_logging"  # New constant for detailed logging option

LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_ERROR = "error"

DIAGNOSTIC_PLC_VERSION = "plc_version"
DIAGNOSTIC_SERVER_VERSION = "server_version"
DIAGNOSTIC_EPSNET_VERSION = "epsnet_version"
DIAGNOSTIC_CONNECTED_CLIENTS = "connected_clients"
DIAGNOSTIC_ACTIVE_VARIABLES = "active_variables"