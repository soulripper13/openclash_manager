# OpenClash Manager

Home Assistant custom integration for managing and switching OpenClash configurations on OpenWrt routers via SSH.

## Features

- **Config Switching**: Select and apply different Clash YAML configurations.
- **Master Switch**: Enable or disable OpenClash globally.
- **Operation Mode**: Quickly switch between `rule`, `global`, and `direct` modes.
- **Service Control**: Restart OpenClash directly from Home Assistant.
- **Updates**: Trigger subscription and core updates.
- **Status Monitoring**: Real-time status sensor (running/stopped) and version information.
- **HomeKit Friendly**: Automatically creates individual switches for each configuration file, making it easy to expose specific configs to Apple Home.

## How it works

The integration connects to your OpenWrt router over SSH and uses `uci` commands and service scripts to manage OpenClash.

- **Config Switching**: Sets `openclash.config.config_path` and restarts the service.
- **Mode Switching**: Sets `openclash.config.operation_mode`.
- **Master Toggle**: Sets `openclash.config.enable`.

## Install

Copy `custom_components/openclash_manager` into your Home Assistant `custom_components` directory, then restart Home Assistant.

## Setup

In Home Assistant, go to **Settings > Devices & services > Add integration** and search for **OpenClash Manager**.

Default settings:

- SSH port: `22`
- SSH username: `root`
- Config directory: `/etc/openclash/config`
- Restart command: `/etc/init.d/openclash restart`

The SSH user needs permission to run `uci`, read the config directory, and restart OpenClash.

## Dashboard

After setup, you can use the built-in entities in your dashboard. The integration also auto-registers a custom dashboard card resource (if available in `www/`) at:

```text
/openclash_manager/openclash-config-card.js
```

## Apple Home (HomeKit)

The integration creates one `switch` entity for each Clash config file. In the HomeKit Bridge options, include these generated switch entities to allow easy switching from Apple Home.

Turn on a config switch in Apple Home to apply that config. Turning off the active config switch is ignored because Clash requires one active config.
