"""
Constants module for NetGrid.

This module contains constants and configuration values used throughout
the NetGrid application to ensure consistency and reduce redundancy.
"""

# Virtual interface prefixes and names that are typically filtered out
VIRTUAL_INTERFACE_PREFIXES = ("veth", "br-", "docker", "virbr")
VIRTUAL_INTERFACE_NAMES = ("lo", "vmsgohere")
VIRTUAL_INTERFACE_TAILSCALE_PREFIX = "tailscale"

# IP configuration types
IP_CONFIG_DHCP = "DHCP"
IP_CONFIG_STATIC = "Static"
IP_CONFIG_UNKNOWN = "Unknown"

# Default values
DEFAULT_SORT_BY = "name"
DEFAULT_COLOR_SCHEME = "default"
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

# Timeout values (in seconds)
SUBPROCESS_TIMEOUT = 5
ETHPOOL_TIMEOUT = 3
DHCP_CHECK_TIMEOUT = 1
NETWORKMANAGER_TIMEOUT = 2

# File paths
DEFAULT_CACHE_DIR = "~/.netgrid/cache"
DEFAULT_VENDOR_CACHE_DIR = "~/.netgrid/vendor_cache"

# OUI database sources
OUI_SOURCES = [
    "https://api.macvendors.com/",
    "https://api.macaddress.io/v1?apiKey=at_",
]

# Interface type detection patterns
ETHERNET_PATTERNS = ("eno", "ens", "eth", "em")
WIRELESS_PATTERNS = ("wlan", "wifi", "wl")
LOOPBACK_PATTERNS = ("lo",)
VIRTUAL_PATTERNS = ("veth", "br-", "docker", "virbr", "virbr0")

# Table formatting constants
TABLE_TITLE = "Network Interfaces"
TABLE_SUBTITLE = "Network Interface Information"
PANEL_TITLE = "NetGrid"

# Error messages
ERROR_INVALID_COLOR_SCHEME = "Invalid color scheme '{scheme}'"
ERROR_INIT_COLLECTOR = "Error initializing interface collector: {error}"
ERROR_DISPLAY_INTERFACES = "Error displaying interfaces: {error}"
ERROR_NO_INTERFACES = "No network interfaces found (after filtering)."

# Warning messages
WARNING_VENDOR_LOOKUP_DISABLED = "Warning: Vendor lookup disabled due to error: {error}"
WARNING_IP_COMMAND_FAILED = "Warning: Failed to run 'ip -j addr show': {error}"
WARNING_COLLECT_INTERFACES = "Warning: Failed to collect interfaces: {error}"
WARNING_POPULATE_VENDORS = "Warning: Failed to populate vendors: {error}" 