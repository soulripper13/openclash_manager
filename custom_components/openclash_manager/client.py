"""SSH client for OpenClash config switching."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import posixpath
import shlex
from typing import Any

import paramiko

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME

from .const import (
    CONF_CONFIG_DIRECTORY,
    CONF_RESTART_COMMAND,
    DEFAULT_CONFIG_DIRECTORY,
    DEFAULT_PORT,
    DEFAULT_RESTART_COMMAND,
    DEFAULT_USERNAME,
    SSH_COMMAND_TIMEOUT,
    SSH_CONNECT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class OpenClashError(Exception):
    """Base OpenClash client error."""


class OpenClashCannotConnectError(OpenClashError):
    """Raised when the router cannot be reached."""


class OpenClashAuthError(OpenClashError):
    """Raised when SSH authentication fails."""


class OpenClashCommandError(OpenClashError):
    """Raised when a router command fails."""


@dataclass(frozen=True)
class OpenClashState:
    """OpenClash state including selectable configs and status."""

    current: str | None
    options: tuple[str, ...]
    enabled: bool
    is_running: bool
    operation_mode: str | None
    version: str | None


@dataclass(frozen=True)
class OpenClashConnectionConfig:
    """SSH connection settings for OpenClash."""

    host: str
    port: int = DEFAULT_PORT
    username: str = DEFAULT_USERNAME
    password: str | None = None
    config_directory: str = DEFAULT_CONFIG_DIRECTORY
    restart_command: str = DEFAULT_RESTART_COMMAND

    @classmethod
    def from_config_entry(cls, entry: ConfigEntry) -> "OpenClashConnectionConfig":
        """Create connection config from a Home Assistant config entry."""
        data: dict[str, Any] = dict(entry.data)
        password = data.get(CONF_PASSWORD) or None
        return cls(
            host=data[CONF_HOST],
            port=int(data.get(CONF_PORT, DEFAULT_PORT)),
            username=data.get(CONF_USERNAME, DEFAULT_USERNAME),
            password=password,
            config_directory=data.get(CONF_CONFIG_DIRECTORY, DEFAULT_CONFIG_DIRECTORY),
            restart_command=data.get(CONF_RESTART_COMMAND, DEFAULT_RESTART_COMMAND),
        )


class OpenClashClient:
    """Small SSH wrapper around OpenClash UCI commands."""

    def __init__(self, config: OpenClashConnectionConfig) -> None:
        """Initialize the client."""
        self._config = config

    def get_state(self) -> OpenClashState:
        """Fetch available configs and active config."""
        with self._connect() as ssh:
            options = self._list_configs(ssh)
            
            # Fetch the entire config section, running status, and package version
            commands = [
                "uci -q show openclash.config || true",
                'ps -w | grep "openclash/clash" | grep -v grep >/dev/null && echo "1" || echo "0"',
                "opkg list-installed luci-app-openclash 2>/dev/null | awk '{print $3}' || echo ''",
            ]
            sep = "OC_SEP"
            combined_command = f"; echo {sep}; ".join(commands)
            output = self._run_command(ssh, f"{combined_command}; echo {sep}")
            
            parts = [p.strip() for p in output.split(sep)]
            uci_raw = parts[0] if len(parts) > 0 else ""
            is_running = (parts[1].strip() == "1") if len(parts) > 1 else False
            opkg_version = parts[2] if len(parts) > 2 else ""

            def find_uci_value(key_suffix: str) -> str | None:
                """Find a value in the uci show output."""
                for line in uci_raw.splitlines():
                    if f"openclash.config.{key_suffix}=" in line:
                        if "=" in line:
                            return line.split("=", 1)[1].strip("'\" ")
                return None

            current_path = find_uci_value("config_path") or ""
            enabled = find_uci_value("enable") == "1"
            
            # The diagnostics confirmed 'operation_mode' exists
            operation_mode = find_uci_value("operation_mode") or find_uci_value("proxy_mode")
            
            # Version detection: use opkg version as discovered
            version = opkg_version or find_uci_value("clash_version")

        current = self._resolve_current_option(current_path, options)

        return OpenClashState(
            current=current,
            options=tuple(options),
            enabled=enabled,
            is_running=is_running,
            operation_mode=operation_mode,
            version=version,
        )

    def switch_config(self, option: str) -> None:
        """Switch OpenClash to the selected config file."""
        with self._connect() as ssh:
            options = self._list_configs(ssh)
            if option not in options:
                raise OpenClashCommandError(f"Unknown OpenClash config: {option}")

            config_path = posixpath.join(self._config.config_directory.rstrip("/"), option)
            set_command = " && ".join(
                (
                    f"uci -q set openclash.config.config_path={shlex.quote(config_path)}",
                    "uci -q commit openclash",
                    self._config.restart_command,
                )
            )
            self._run_command(ssh, set_command, timeout=SSH_COMMAND_TIMEOUT)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable OpenClash."""
        value = "1" if enabled else "0"
        command = f"uci -q set openclash.config.enable={value} && uci -q commit openclash && {self._config.restart_command}"
        with self._connect() as ssh:
            self._run_command(ssh, command, timeout=SSH_COMMAND_TIMEOUT)

    def set_operation_mode(self, mode: str) -> None:
        """Set OpenClash operation mode (e.g., redoir, fake-ip, tun)."""
        command = f"uci -q set openclash.config.operation_mode={shlex.quote(mode)} && uci -q commit openclash && {self._config.restart_command}"
        with self._connect() as ssh:
            self._run_command(ssh, command, timeout=SSH_COMMAND_TIMEOUT)

    def update_subscriptions(self) -> None:
        """Trigger OpenClash subscription update."""
        command = "/usr/share/openclash/openclash_update.sh"
        with self._connect() as ssh:
            self._run_command(ssh, command, timeout=SSH_COMMAND_TIMEOUT)

    def update_cores(self) -> None:
        """Trigger OpenClash core update."""
        command = "/usr/share/openclash/openclash_core.sh"
        with self._connect() as ssh:
            self._run_command(ssh, command, timeout=SSH_COMMAND_TIMEOUT)

    def restart_openclash(self) -> None:
        """Restart the OpenClash service."""
        with self._connect() as ssh:
            self._run_command(ssh, self._config.restart_command, timeout=SSH_COMMAND_TIMEOUT)

    def _connect(self) -> paramiko.SSHClient:
        """Open an SSH connection to the router."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                hostname=self._config.host,
                port=self._config.port,
                username=self._config.username,
                password=self._config.password,
                timeout=SSH_CONNECT_TIMEOUT,
                banner_timeout=SSH_CONNECT_TIMEOUT,
                auth_timeout=SSH_CONNECT_TIMEOUT,
                allow_agent=self._config.password is None,
                look_for_keys=self._config.password is None,
                compress=True,
            )
        except paramiko.AuthenticationException as err:
            raise OpenClashAuthError("SSH authentication failed") from err
        except (paramiko.SSHException, OSError) as err:
            raise OpenClashCannotConnectError("Could not connect to OpenClash router") from err

        return ssh

    def _list_configs(self, ssh: paramiko.SSHClient) -> list[str]:
        """List selectable OpenClash config files."""
        raw_config_dir = self._config.config_directory.rstrip("/")
        config_dir = shlex.quote(raw_config_dir)
        command = (
            f"dir={config_dir}; "
            '[ -d "$dir" ] || exit 0; '
            'find "$dir" -type f \\( -name "*.yaml" -o -name "*.yml" \\) 2>/dev/null '
            '| while IFS= read -r file; do '
            'file="${file#$dir/}"; '
            'printf "%s\\n" "$file"; '
            "done | sort -u"
        )
        output = self._run_command(ssh, command)
        return [line.strip() for line in output.splitlines() if line.strip()]

    def _resolve_current_option(
        self,
        current_path: str,
        options: list[str],
    ) -> str | None:
        """Resolve the UCI config path to one of the selectable options."""
        if not current_path:
            return None

        clean_path = current_path.strip().strip("'\"")
        config_dir = self._config.config_directory.rstrip("/")

        candidates = [clean_path]
        if clean_path.startswith(f"{config_dir}/"):
            candidates.append(clean_path.removeprefix(f"{config_dir}/"))
        candidates.append(posixpath.basename(clean_path))

        for candidate in candidates:
            if candidate in options:
                return candidate

        lowered_options = {option.lower(): option for option in options}
        for candidate in candidates:
            match = lowered_options.get(candidate.lower())
            if match:
                return match

        _LOGGER.warning(
            "OpenClash active config %r was not found in discovered options: %s",
            current_path,
            options,
        )
        return None

    def _run_command(
        self,
        ssh: paramiko.SSHClient,
        command: str,
        timeout: int = SSH_COMMAND_TIMEOUT,
    ) -> str:
        """Run a shell command on the router."""
        _LOGGER.debug("Running OpenClash command: %s", command)
        try:
            _stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode("utf-8", errors="replace")
            error = stderr.read().decode("utf-8", errors="replace")
        except (paramiko.SSHException, OSError) as err:
            raise OpenClashCommandError("OpenClash SSH command failed") from err

        if exit_code != 0:
            detail = (error or output).strip()
            raise OpenClashCommandError(detail or f"Command exited with {exit_code}")

        return output
