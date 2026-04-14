"""The Maya Commbox integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_IP
from .hub import CommBoxHub
from .coordinator import CommBoxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.BINARY_SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Maya Commbox from a config entry."""
    ip_address = entry.data[CONF_IP]
    session = async_get_clientsession(hass)
    hub = CommBoxHub(ip_address, session)
    
    device_info = await hub.get_device_info()
    
    coordinator = CommBoxDataUpdateCoordinator(hass, hub)
    coordinator.device_info = device_info
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
