"""Hub for Maya Commbox integration."""
import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

class CommBoxHub:
    """Wrapper class for Maya Commbox HTTP API."""

    def __init__(self, ip_address, session):
        """Initialize the hub."""
        self.ip_address = ip_address
        self.session = session
        self.base_url = f"http://{ip_address}"

    async def get_device_info(self):
        """Fetch device information from the module."""
        url = f"{self.base_url}/get_device_info"
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url) as response:
                    if response.status == 200:
                        raw_data = await response.json()
                        data = raw_data.get("data", {})
                        model_code = data.get("model_code", 31)
                        # Mapping based on Maya Commbox manual
                        caps = {
                            31: {"model": "MIO400", "inputs": 4, "outputs": 4},
                            32: {"model": "MIO800", "inputs": 8, "outputs": 8},
                            34: {"model": "MIO2408", "inputs": 24, "outputs": 8},
                            41: {"model": "MIO0816", "inputs": 8, "outputs": 16},
                            40: {"model": "MIO402", "inputs": 4, "outputs": 2},
                        }.get(model_code, {"model": f"MIO (Unknown {model_code})", "inputs": 4, "outputs": 4})
                        
                        return {
                            "model": caps["model"],
                            "num_inputs": caps["inputs"],
                            "num_outputs": caps["outputs"],
                            "firmware": data.get("version_firmware", "Unknown"),
                            "unique_id": data.get("unique_id", self.ip_address)
                        }
        except Exception as err:
            _LOGGER.error("Error fetching device info from %s: %s (%s)", self.ip_address, type(err).__name__, err)
        
        # Fallback to default MIO400 if detection fails
        return {"model": "MIO400", "num_inputs": 4, "num_outputs": 4, "firmware": "Unknown"}

    async def get_io_status(self):
        """Fetch current states from the device."""
        url = f"{self.base_url}/get_io_status"
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url) as response:
                    if response.status == 200:
                        raw_data = await response.json()
                        return raw_data.get("data")
        except Exception as err:
            _LOGGER.warning("Connection failure to Maya Commbox at %s: %s", self.ip_address, err)
        return None

    async def set_output(self, address, state, num_outputs=4):
        """Set a relay state."""
        # MIOv3 API: address is 1-based (1=Relay1, 2=Relay2, etc.)
        # Internal address is 0-based, so add 1 for API call.
        api_address = address + 1
        url = f"{self.base_url}/set_output"
        params = {
            "address": api_address,
            "state": 1 if state else 0
        }
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result") == "sucess"
        except Exception as err:
            _LOGGER.error("Error setting output %s at %s: %s", api_address, self.ip_address, err)
        return False

    async def pulse_output(self, address, time_ms, num_outputs=4):
        """Pulse a relay using the internal timer (time_1)."""
        # MIOv3 API: address is 1-based
        api_address = address + 1
        url = f"{self.base_url}/set_output"
        params = {
            "address": api_address,
            "state": 1,
            "time_1": time_ms
        }
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result") == "sucess"
        except Exception as err:
            _LOGGER.error("Error pulsing output %s at %s: %s", api_address, self.ip_address, err)
        return False

    async def test_connection(self):
        """Test if the device is reachable and returns valid MIO data."""
        data = await self.get_device_info()
        return data.get("firmware") != "Unknown"
