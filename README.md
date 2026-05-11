# OpenClash Manager

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
![Version](https://img.shields.io/badge/version-0.4.0-blue.svg?style=for-the-badge)

OpenClash Manager is a powerful Home Assistant custom integration designed to give you full control over your OpenClash configuration on OpenWrt routers via SSH.

## Features

- **🚀 Smart Config Switching**: Select and apply different Clash YAML configurations. Switch names are automatically cleaned up (removing `.yaml`) for a polished look.
- **🛡️ Enable Toggle**: Turn OpenClash on or off globally with a simple switch.
- **📡 Operation Modes**: Quickly switch between `Rule`, `Global`, and `Direct` modes.
- **🔄 Service Control**: Restart OpenClash directly from Home Assistant buttons.
- **🆙 Automatic Updates**: Trigger subscription updates and core updates from your dashboard.
- **📶 Status Monitoring**: Real-time status sensor using the `CONNECTIVITY` class (perfect for HomeKit).
- **🍏 Apple Home (HomeKit) Optimized**: 
    - Entities are named and categorized for the best Apple Home experience.
    - Group multiple config switches into a single tile for a "Pro" device feel.
    - Includes a **Configuration URL** link directly to your router's OpenClash Luci dashboard.

## Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Click the three dots in the top right and select **Custom repositories**.
3. Add `https://github.com/soulripper13/openclash_manager` with the category **Integration**.
4. Click **Install**.
5. Restart Home Assistant.

### Method 2: Manual

1. Download the latest release.
2. Copy the `custom_components/openclash_manager` folder to your HA `custom_components` directory.
3. Restart Home Assistant.

## Configuration

1. Go to **Settings > Devices & Services**.
2. Click **Add Integration** and search for **OpenClash Manager**.
3. Enter your router's SSH details:
    - **Host**: Your router's IP address.
    - **Port**: SSH port (default `22`).
    - **Username**: SSH username (usually `root`).
    - **Password**: SSH password.
    - **Config Directory**: Path to your Clash configs (default `/etc/openclash/config`).
    - **Restart Command**: The command used to restart OpenClash (default `/etc/init.d/openclash restart`).

## Usage in Apple Home

To get the best experience in Apple Home:
1. Add the **HomeKit Bridge** integration in Home Assistant.
2. Include the `switch.enable` and all `switch.*_config` entities.
3. In the Apple Home app, long-press the **Enable** tile and select **Group with Other Accessories**.
4. Group all OpenClash-related switches together. This creates a single professional-looking tile that expands to show all controls.

## License

MIT License. See [LICENSE](LICENSE) for details.
