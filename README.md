# CommBox MIO Home Assistant Integration

Custom integration to control and monitor CommBox MIO series modules (specifically MIO400v3) using the JSON HTTP API.

## Features

- **Switches**: Control relays 1-4.
- **Binary Sensors**: Monitor digital inputs 1-4.
- **Services**: `pulse_output` service for precise relay pulsing.

## Installation

1. Open HACS in Home Assistant.
2. Go to "Integrations".
3. Click the three dots in the top right corner and select "Custom repositories".
4. Add the URL of this repository and select "Integration" as the category.
5. Search for "CommBox MIO" and click Download.
6. Restart Home Assistant.
7. Go to Settings -> Devices & Services -> Add Integration -> "CommBox MIO".

## Requirements

- **Firmware**: Version 3.02 or higher (supports JSON API).
- **Network**: Module must be accessible via Static IP or DHCP reservation.

## Configuration

During setup, you only need to provide the **IP Address** of your CommBox module.

---
Created by Antigravity AI.
