from homeassistant.const import Platform

DOMAIN = "ziggo_modem"

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_VERBOSE_DIAGNOSTICS = "verbose_diagnostics"

DEFAULT_HOST = "192.168.100.1"
DEFAULT_PORT = 443
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_VERBOSE_DIAGNOSTICS = False

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
]
