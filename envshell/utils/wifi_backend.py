import subprocess
from typing import List, Dict
from loguru import logger
import re


"""
Thanks to @kaipark for the following code.
"""

def get_wifi_status() -> bool:
    """Get WiFi power status

    Returns:
        bool: True if WiFi is enabled, False otherwise
    """
    try:
        result = subprocess.run(
            ["nmcli", "radio", "wifi"], capture_output=True, text=True
        )
        return result.stdout.strip().lower() == "enabled"
    except Exception as e:
        logger.error(f"Failed getting WiFi status: {e}")
        return False


def set_wifi_power(enabled: bool) -> None:
    """Set WiFi power state

    Args:
        enabled (bool): True to enable, False to disable
    """
    try:
        state = "on" if enabled else "off"
        subprocess.run(["nmcli", "radio", "wifi", state], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed setting WiFi power: {e}")


def get_wifi_networks() -> List[Dict[str, str]]:
    """Get list of available WiFi networks

    Returns:
        List[Dict[str, str]]: List of network dictionaries
    """
    try:
        # Check if WiFi is supported on this system
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE", "device"],
            capture_output=True,
            text=True,
        )
        wifi_interfaces = [line for line in result.stdout.split("\n") if "wifi" in line]
        if not wifi_interfaces:
            logger.warning("WiFi is not supported on this machine")
            return []

        # Use --terse mode and specific fields for more reliable parsing
        result = subprocess.run(
            [
                "nmcli",
                "-t",
                "-f",
                "IN-USE,SSID,SIGNAL,SECURITY",
                "device",
                "wifi",
                "list",
            ],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        networks = []
        for line in output.split("\n"):
            if not line.strip():
                continue
            # Split by ':' since we're using terse mode
            parts = line.split(":")
            if len(parts) >= 4:
                in_use = "*" in parts[0]
                ssid = parts[1]
                signal = parts[2] if parts[2].strip() else "0"
                security = parts[3] if parts[3].strip() != "" else "none"
                # Only add networks with valid SSIDs
                if ssid and ssid.strip():
                    networks.append(
                        {
                            "in_use": in_use,
                            "ssid": ssid.strip(),
                            "signal": signal.strip(),
                            "security": security.strip(),
                        }
                    )
        networks = sorted(
            networks, key=lambda network: ((not network["in_use"]), network["ssid"])
        )
        return networks
    except Exception as e:
        logger.error(f"Failed getting WiFi networks: {e}")
        return []


def get_connection_info(ssid: str) -> Dict[str, str]:
    """Get information about a WiFi connection

    Args:
        ssid (str): Network SSID

    Returns:
        Dict[str, str]: Dictionary containing connection information
    """
    try:
        result = subprocess.run(
            ["nmcli", "-t", "connection", "show", ssid], capture_output=True, text=True
        )
        output = result.stdout
        info = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info
    except Exception as e:
        logger.error(f"Failed getting connection info: {e}")
        return {}


def connect_network(ssid: str, password: str = "", remember: bool = True) -> bool:
    """Connect to a WiFi network

    Args:
        ssid (str): Network SSID
        password (str, optional): Network password. Defaults to None.
        remember (bool, optional): Whether to save the connection. Defaults to True.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # First try to connect using saved connection
        try:
            subprocess.run(["nmcli", "con", "up", ssid], check=True)
            return True
        except subprocess.CalledProcessError:
            # If saved connection fails, try with password if provided
            if password:
                cmd = ["nmcli", "device", "wifi", "connect", ssid, "password", password]
                if not remember:
                    cmd.extend(["--temporary"])
                subprocess.run(cmd, check=True)
                return True
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed connecting to network: {e}")
        return False


def disconnect_network(ssid: str) -> bool:
    """Disconnect from a WiFi network

    Args:
        ssid (str): Network SSID

    Returns:
        bool: True if disconnection successful, False otherwise
    """
    try:
        subprocess.run(["nmcli", "connection", "down", ssid], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed disconnecting from network: {e}")
        return False


def forget_network(ssid: str) -> bool:
    """Remove a saved WiFi network

    Args:
        ssid (str): Network SSID

    Returns:
        bool: True if removal successful, False otherwise
    """
    try:
        subprocess.run(["nmcli", "connection", "delete", ssid], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed removing network: {e}")
        return False


def get_network_speed() -> Dict[str, float]:
    """Get current network speed

    Returns:
        Dict[str, float]: Dictionary with upload and download speeds in Mbps
    """
    try:
        # Get WiFi interface name
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE", "device"],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        wifi_lines = [line for line in output.split("\n") if "wifi" in line]

        if not wifi_lines:
            # Return zeros with the expected keys when WiFi is not supported
            logger.warning("WiFi is not supported on this machine")
            return {"rx_bytes": 0, "tx_bytes": 0, "wifi_supported": False}

        interface = wifi_lines[0].split(":")[0]

        # Get current bytes
        with open(f"/sys/class/net/{interface}/statistics/rx_bytes") as f:
            rx_bytes = int(f.read())
        with open(f"/sys/class/net/{interface}/statistics/tx_bytes") as f:
            tx_bytes = int(f.read())
        return {"rx_bytes": rx_bytes, "tx_bytes": tx_bytes, "wifi_supported": True}
    except Exception as e:
        logger.error(f"Failed getting network speed: {e}")
        return {"rx_bytes": 0, "tx_bytes": 0, "wifi_supported": False}


def remove_ansi(text):
    return re.sub(r"\x1b\[[0-9;]*m", "", text)

def fetch_currently_connected_ssid() -> str | None:
    # Second approach: Try checking all active WiFi connections
    active_connections = subprocess.getoutput(
        "nmcli -t -f NAME,TYPE con show --active"
    ).split("\n")
    print(f"Debug - all active connections: {active_connections}")

    for conn in active_connections:
        if ":" in conn and (
            "wifi" in conn.lower() or "802-11-wireless" in conn.lower()
        ):
            connection_name = conn.split(":")[0]
            print(f"Debug - Found WiFi connection from active list: {connection_name}")
            return remove_ansi(connection_name)

        else:
            return None