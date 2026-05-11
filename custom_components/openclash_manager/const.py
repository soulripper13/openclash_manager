"""Constants for the OpenClash Config Switcher integration."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME

DOMAIN = "openclash_manager"

CONF_CONFIG_DIRECTORY = "config_directory"
CONF_RESTART_COMMAND = "restart_command"

DEFAULT_PORT = 22
DEFAULT_USERNAME = "root"
DEFAULT_CONFIG_DIRECTORY = "/etc/openclash/config"
DEFAULT_RESTART_COMMAND = "/etc/init.d/openclash restart"

DATA_COORDINATOR = "coordinator"

SSH_CONNECT_TIMEOUT = 10
SSH_COMMAND_TIMEOUT = 60

CONFIG_KEYS = {
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_CONFIG_DIRECTORY,
    CONF_RESTART_COMMAND,
}
