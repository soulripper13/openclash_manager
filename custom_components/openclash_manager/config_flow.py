"""Config flow for OpenClash Config Switcher."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .client import (
    OpenClashAuthError,
    OpenClashCannotConnectError,
    OpenClashClient,
    OpenClashCommandError,
    OpenClashConnectionConfig,
)
from .const import (
    CONF_CONFIG_DIRECTORY,
    CONF_RESTART_COMMAND,
    DEFAULT_CONFIG_DIRECTORY,
    DEFAULT_PORT,
    DEFAULT_RESTART_COMMAND,
    DEFAULT_USERNAME,
    DOMAIN,
)


def _schema(user_input: dict[str, Any] | None = None) -> vol.Schema:
    """Return the user step schema."""
    values = user_input or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=values.get(CONF_HOST, "")): str,
            vol.Optional(CONF_PORT, default=values.get(CONF_PORT, DEFAULT_PORT)): int,
            vol.Optional(
                CONF_USERNAME,
                default=values.get(CONF_USERNAME, DEFAULT_USERNAME),
            ): str,
            vol.Optional(CONF_PASSWORD, default=values.get(CONF_PASSWORD, "")): str,
            vol.Optional(
                CONF_CONFIG_DIRECTORY,
                default=values.get(CONF_CONFIG_DIRECTORY, DEFAULT_CONFIG_DIRECTORY),
            ): str,
            vol.Optional(
                CONF_RESTART_COMMAND,
                default=values.get(CONF_RESTART_COMMAND, DEFAULT_RESTART_COMMAND),
            ): str,
        }
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> str:
    """Validate the user input allows us to connect."""
    config = OpenClashConnectionConfig(
        host=data[CONF_HOST],
        port=int(data.get(CONF_PORT, DEFAULT_PORT)),
        username=data.get(CONF_USERNAME, DEFAULT_USERNAME),
        password=data.get(CONF_PASSWORD) or None,
        config_directory=data.get(CONF_CONFIG_DIRECTORY, DEFAULT_CONFIG_DIRECTORY),
        restart_command=data.get(CONF_RESTART_COMMAND, DEFAULT_RESTART_COMMAND),
    )
    client = OpenClashClient(config)

    try:
        state = await hass.async_add_executor_job(client.get_state)
    except OpenClashAuthError as err:
        raise InvalidAuth from err
    except OpenClashCannotConnectError as err:
        raise CannotConnect from err
    except OpenClashCommandError as err:
        raise CannotReadConfigs(str(err)) from err

    if not state.options:
        raise CannotReadConfigs("No YAML configs were found")

    return f"OpenClash {data[CONF_HOST]}"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenClash Config Switcher."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()
            user_input[CONF_USERNAME] = user_input.get(CONF_USERNAME, DEFAULT_USERNAME).strip()
            user_input[CONF_CONFIG_DIRECTORY] = user_input.get(
                CONF_CONFIG_DIRECTORY, DEFAULT_CONFIG_DIRECTORY
            ).rstrip("/")
            user_input[CONF_RESTART_COMMAND] = user_input.get(
                CONF_RESTART_COMMAND, DEFAULT_RESTART_COMMAND
            ).strip()

            try:
                title = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotReadConfigs:
                errors["base"] = "cannot_read_configs"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input.get(CONF_PORT, DEFAULT_PORT)}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid auth."""


class CannotReadConfigs(HomeAssistantError):
    """Error to indicate configs cannot be read."""
