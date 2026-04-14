# Maya Commbox Home Assistant Integration

Custom integration to control and monitor Maya Commbox (CommBox MIO series) modules using the JSON HTTP API.

## Features
- **Dynamic Detection**: Automatically detects module model (MIO400, MIO800, etc.).
- **Relay Control**: Switches for all physical relays.
- **Input Monitoring**: Binary sensors for all physical inputs.
- **Pulse Service**: Entity-based pulse service for relays.

## Installation
1. Ensure your CommBox module is on the same network as Home Assistant.
2. Copy the `custom_components/maya_commbox` directory to your HA `custom_components` folder.
3. Restart Home Assistant.
4. Go to Settings -> Devices & Services -> Add Integration -> "Maya Commbox".
5. Enter the IP address of the module.

---

## Commercial Support & Credits

Esta integração foi desenvolvida para os módulos **CommBox MIO** em parceria com:

- **[Hiperenge](https://www.hiperenge.com.br)**: Soluções em engenharia e automação.
- **[Maya Home](https://www.mayahome.ia.br)**: Inteligência artificial e automação residencial premium.
