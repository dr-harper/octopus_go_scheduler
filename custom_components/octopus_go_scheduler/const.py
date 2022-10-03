"""Constants for carbon intensity."""
# Base component constants
NAME = "Octopus Go Scheduler"
DOMAIN = "octopus_go_scheduler"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.2.0"

ISSUE_URL = "https://github.com/jscruz/sensor.octopus_go_scheduler/issues"

# Icons
ICON = "mdi:leaf"
LOW_ICON = "mdi:leaf"
MODERATE_ICON = "mdi:factory"
HIGH_ICON = "mdi:smog"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_POSTCODE = "postcode"

# Defaults
DEFAULT_NAME = DOMAIN

INTENSITY = {
    "very low" : 0,
    "low" : 1,
    "moderate": 2,
    "high": 3,
    "very high": 4,
}

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
