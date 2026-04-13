"""Hub for CommBox MIO integration."""
import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

class CommBoxHub:
    """Wrapper class for CommBox MIO HTTP API."""

    def __init__(self, ip_address):
        """Initialize the hub."""
        self.ip_address = ip_address
        self.base_url = f"http://{ip_address}"

    async def get_device_info(self):
        """Fetch device information from the module."""
        url = f"{self.base_url}/get_device_info"
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(10):
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            model_code = data.get("model_code", 31)
                            # Mapping based on manual
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
                                "firmware": data.get("firmware_version", "Unknown")
                            }
        except Exception as err:
            _LOGGER.error("Error fetching device info from %s: %s", self.ip_address, err)
        return {"model": "MIO400", "num_inputs": 4, "num_outputs": 4, "firmware": "Unknown"}

    async def get_io_status(self):
        """Fetch current states from the device."""
        url = f"{self.base_url}/get_io_status"
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(10):
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
        except Exception as err:
            _LOGGER.error("Error connecting to CommBox at %s: %s", self.ip_address, err)
        return None

    async def set_output(self, address, state, num_outputs=4):
        """Set a relay state. Physical Output 1 is at index 31."""
        # Mapping: Physical Output 1 -> Index 31, Output 2 -> 30, etc.
        api_address = 32 - num_outputs + address
        url = f"{self.base_url}/set_output"
        params = {
            "address": api_address,
            "state": 1 if state else 0
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(10):
                    async with session.get(url, params=params) as response:
                        return response.status == 200
        except Exception as err:
            _LOGGER.error("Error setting output at %s: %s", self.ip_address, err)
        return False

    async def pulse_output(self, address, time_ms):
        """Pulse a relay (uses time_1 internal timer if available, otherwise manual)."""
        # Note: The manual mentions set_output?address=X&state=1&time_1=Y
        url = f"{self.base_url}/set_output"
        params = {
            "address": address,
            "state": 1,
            "time_1": time_ms
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(10):
                    async with session.get(url, params=params) as response:
                        return response.status == 200
        except Exception as err:
            _LOGGER.error("Error pulsing output at %s: %s", self.ip_address, err)
        return False

    async def test_connection(self):
        """Test if the device is reachable."""
        # Some modules have a /get_device_info or similar, but /get_io_status is reliable
        return await self.get_io_status() is not None
