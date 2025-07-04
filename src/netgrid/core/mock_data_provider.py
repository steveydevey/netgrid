"""
Mock data provider for network interface testing.

This module provides realistic mock data for testing NetGrid in isolated environments
like containers where real network interfaces may not be available.
"""

import os
import random
from typing import List, Dict, Optional, Any
from .data_models import (
    NetworkInterface,
    InterfaceCollection,
    InterfaceType,
    LinkState,
    DuplexMode,
)


class MockDataProvider:
    """
    Provides mock network interface data for testing purposes.
    
    This class generates realistic interface data that mimics what would be found
    on real systems, including various types of interfaces, vendors, and configurations.
    """
    
    # Real-world interface configurations for different scenarios
    MOCK_INTERFACES = [
        {
            "name": "eth0",
            "mac_address": "52:54:00:12:34:56",
            "ip_addresses": ["192.168.1.100", "fe80::5054:ff:fe12:3456"],
            "link_state": LinkState.UP,
            "speed": 1000,
            "duplex": DuplexMode.FULL,
            "mtu": 1500,
            "driver": "virtio_net",
            "interface_type": InterfaceType.PHYSICAL,
            "vendor": "Red Hat Inc.",
            "description": "Primary network interface",
            "flags": ["UP", "BROADCAST", "RUNNING", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "eth1",
            "mac_address": "08:00:27:ab:cd:ef",
            "ip_addresses": ["10.0.0.50"],
            "link_state": LinkState.UP,
            "speed": 100,
            "duplex": DuplexMode.FULL,
            "mtu": 1500,
            "driver": "e1000",
            "interface_type": InterfaceType.PHYSICAL,
            "vendor": "Intel Corporation",
            "description": "Secondary network interface",
            "flags": ["UP", "BROADCAST", "RUNNING", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "wlan0",
            "mac_address": "24:f5:aa:11:22:33",
            "ip_addresses": ["192.168.0.105", "fe80::26f5:aaff:fe11:2233"],
            "link_state": LinkState.UP,
            "speed": 54,
            "duplex": DuplexMode.HALF,
            "mtu": 1500,
            "driver": "iwlwifi",
            "interface_type": InterfaceType.WIRELESS,
            "vendor": "Intel Corporation",
            "description": "Wireless interface",
            "flags": ["UP", "BROADCAST", "RUNNING", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "enp0s3",
            "mac_address": "08:00:27:44:55:66",
            "ip_addresses": ["172.16.1.20"],
            "link_state": LinkState.UP,
            "speed": 1000,
            "duplex": DuplexMode.FULL,
            "mtu": 1500,
            "driver": "e1000",
            "interface_type": InterfaceType.PHYSICAL,
            "vendor": "Intel Corporation",
            "description": "Ethernet interface (systemd naming)",
            "flags": ["UP", "BROADCAST", "RUNNING", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "enp0s8",
            "mac_address": "08:00:27:77:88:99",
            "ip_addresses": [],
            "link_state": LinkState.DOWN,
            "speed": None,
            "duplex": DuplexMode.UNKNOWN,
            "mtu": 1500,
            "driver": "e1000",
            "interface_type": InterfaceType.PHYSICAL,
            "vendor": "Intel Corporation",
            "description": "Disconnected ethernet interface",
            "flags": ["BROADCAST", "MULTICAST"],
            "extra_data": {"carrier": "0", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "bond0",
            "mac_address": "52:54:00:aa:bb:cc",
            "ip_addresses": ["10.1.1.10"],
            "link_state": LinkState.UP,
            "speed": 2000,
            "duplex": DuplexMode.FULL,
            "mtu": 1500,
            "driver": "bonding",
            "interface_type": InterfaceType.BOND,
            "vendor": None,
            "description": "Bond interface",
            "flags": ["UP", "BROADCAST", "RUNNING", "MASTER", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "br0",
            "mac_address": "52:54:00:dd:ee:ff",
            "ip_addresses": ["192.168.100.1"],
            "link_state": LinkState.UP,
            "speed": None,
            "duplex": DuplexMode.UNKNOWN,
            "mtu": 1500,
            "driver": "bridge",
            "interface_type": InterfaceType.BRIDGE,
            "vendor": None,
            "description": "Bridge interface",
            "flags": ["UP", "BROADCAST", "RUNNING", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "eth0.100",
            "mac_address": "52:54:00:12:34:56",
            "ip_addresses": ["10.100.1.5"],
            "link_state": LinkState.UP,
            "speed": 1000,
            "duplex": DuplexMode.FULL,
            "mtu": 1500,
            "driver": "virtio_net",
            "interface_type": InterfaceType.VLAN,
            "vendor": "Red Hat Inc.",
            "description": "VLAN 100 interface",
            "flags": ["UP", "BROADCAST", "RUNNING", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "lo",
            "mac_address": None,
            "ip_addresses": ["127.0.0.1", "::1"],
            "link_state": LinkState.UP,
            "speed": None,
            "duplex": DuplexMode.UNKNOWN,
            "mtu": 65536,
            "driver": None,
            "interface_type": InterfaceType.LOOPBACK,
            "vendor": None,
            "description": "Loopback interface",
            "flags": ["UP", "LOOPBACK", "RUNNING"],
            "extra_data": {"carrier": "1", "device_type": "772", "tx_queue_len": "1000"}
        },
        {
            "name": "tun0",
            "mac_address": None,
            "ip_addresses": ["10.8.0.2"],
            "link_state": LinkState.UP,
            "speed": None,
            "duplex": DuplexMode.UNKNOWN,
            "mtu": 1500,
            "driver": "tun",
            "interface_type": InterfaceType.VIRTUAL,
            "vendor": None,
            "description": "VPN tunnel interface",
            "flags": ["UP", "POINTOPOINT", "RUNNING", "NOARP", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "65534", "tx_queue_len": "500"}
        }
    ]
    
    # Additional virtual interfaces that are typically filtered out
    VIRTUAL_INTERFACES = [
        {
            "name": "veth0abc123",
            "mac_address": "02:42:ac:11:00:02",
            "ip_addresses": [],
            "link_state": LinkState.UP,
            "speed": 10000,
            "duplex": DuplexMode.FULL,
            "mtu": 1500,
            "driver": "veth",
            "interface_type": InterfaceType.VIRTUAL,
            "vendor": None,
            "description": "Docker veth interface",
            "flags": ["UP", "BROADCAST", "RUNNING", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "br-docker0",
            "mac_address": "02:42:12:34:56:78",
            "ip_addresses": ["172.17.0.1"],
            "link_state": LinkState.UP,
            "speed": None,
            "duplex": DuplexMode.UNKNOWN,
            "mtu": 1500,
            "driver": "bridge",
            "interface_type": InterfaceType.BRIDGE,
            "vendor": None,
            "description": "Docker bridge",
            "flags": ["UP", "BROADCAST", "RUNNING", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "1", "tx_queue_len": "1000"}
        },
        {
            "name": "tailscale0",
            "mac_address": None,
            "ip_addresses": ["100.64.0.1"],
            "link_state": LinkState.UP,
            "speed": None,
            "duplex": DuplexMode.UNKNOWN,
            "mtu": 1280,
            "driver": "tun",
            "interface_type": InterfaceType.VIRTUAL,
            "vendor": None,
            "description": "Tailscale VPN interface",
            "flags": ["UP", "POINTOPOINT", "RUNNING", "NOARP", "MULTICAST"],
            "extra_data": {"carrier": "1", "device_type": "65534", "tx_queue_len": "500"}
        }
    ]
    
    def __init__(self, include_virtual: bool = True, include_filtered: bool = False):
        """
        Initialize the mock data provider.
        
        Args:
            include_virtual: Whether to include virtual interfaces like bonds, bridges
            include_filtered: Whether to include normally filtered interfaces (veth, br-, tailscale)
        """
        self.include_virtual = include_virtual
        self.include_filtered = include_filtered
    
    def get_mock_interfaces(self) -> InterfaceCollection:
        """
        Generate a collection of mock network interfaces.
        
        Returns:
            InterfaceCollection with mock interface data
        """
        collection = InterfaceCollection()
        
        # Add main interfaces
        for interface_data in self.MOCK_INTERFACES:
            interface = self._create_interface_from_data(interface_data)
            
            # Filter virtual interfaces if not included
            if not self.include_virtual and interface.interface_type in [
                InterfaceType.VIRTUAL, InterfaceType.BRIDGE, InterfaceType.BOND
            ]:
                continue
                
            collection.add_interface(interface)
        
        # Add filtered interfaces if requested
        if self.include_filtered:
            for interface_data in self.VIRTUAL_INTERFACES:
                interface = self._create_interface_from_data(interface_data)
                collection.add_interface(interface)
        
        return collection
    
    def get_interface_by_name(self, name: str) -> Optional[NetworkInterface]:
        """
        Get a specific mock interface by name.
        
        Args:
            name: Interface name to retrieve
            
        Returns:
            NetworkInterface object if found, None otherwise
        """
        all_data = self.MOCK_INTERFACES + (self.VIRTUAL_INTERFACES if self.include_filtered else [])
        
        for interface_data in all_data:
            if interface_data["name"] == name:
                return self._create_interface_from_data(interface_data)
        
        return None
    
    def get_interface_names(self) -> List[str]:
        """
        Get list of all mock interface names.
        
        Returns:
            List of interface names
        """
        names = [data["name"] for data in self.MOCK_INTERFACES]
        
        if self.include_filtered:
            names.extend([data["name"] for data in self.VIRTUAL_INTERFACES])
        
        return sorted(names)
    
    def _create_interface_from_data(self, data: Dict[str, Any]) -> NetworkInterface:
        """
        Create a NetworkInterface object from mock data.
        
        Args:
            data: Dictionary containing interface data
            
        Returns:
            NetworkInterface object
        """
        return NetworkInterface(
            name=data["name"],
            mac_address=data.get("mac_address"),
            ip_addresses=data.get("ip_addresses", []),
            link_state=data.get("link_state", LinkState.UNKNOWN),
            speed=data.get("speed"),
            duplex=data.get("duplex", DuplexMode.UNKNOWN),
            mtu=data.get("mtu"),
            driver=data.get("driver"),
            interface_type=data.get("interface_type", InterfaceType.UNKNOWN),
            vendor=data.get("vendor"),
            description=data.get("description"),
            flags=data.get("flags", []),
            extra_data=data.get("extra_data", {})
        )
    
    @classmethod
    def create_custom_interface(
        cls,
        name: str,
        mac_address: Optional[str] = None,
        ip_addresses: Optional[List[str]] = None,
        link_state: LinkState = LinkState.UP,
        speed: Optional[int] = None,
        interface_type: InterfaceType = InterfaceType.PHYSICAL,
        vendor: Optional[str] = None,
        **kwargs
    ) -> NetworkInterface:
        """
        Create a custom mock interface with specified parameters.
        
        Args:
            name: Interface name
            mac_address: MAC address (auto-generated if None)
            ip_addresses: List of IP addresses
            link_state: Link state
            speed: Interface speed in Mbps
            interface_type: Type of interface
            vendor: Vendor name
            **kwargs: Additional parameters for NetworkInterface
            
        Returns:
            NetworkInterface object
        """
        if mac_address is None and interface_type == InterfaceType.PHYSICAL:
            # Generate a realistic MAC address
            mac_address = cls._generate_mac_address()
        
        if ip_addresses is None:
            ip_addresses = []
        
        # Set default values for common parameters
        defaults = {
            "duplex": DuplexMode.FULL if speed and speed > 10 else DuplexMode.UNKNOWN,
            "mtu": 1500,
            "driver": "mock_driver",
            "description": f"Mock {interface_type.value} interface",
            "flags": ["UP", "BROADCAST", "RUNNING", "MULTICAST"] if link_state == LinkState.UP else ["BROADCAST", "MULTICAST"],
            "extra_data": {"carrier": "1" if link_state == LinkState.UP else "0", "device_type": "1"}
        }
        
        # Update defaults with provided kwargs
        defaults.update(kwargs)
        
        return NetworkInterface(
            name=name,
            mac_address=mac_address,
            ip_addresses=ip_addresses,
            link_state=link_state,
            speed=speed,
            interface_type=interface_type,
            vendor=vendor,
            **defaults
        )
    
    @staticmethod
    def _generate_mac_address() -> str:
        """
        Generate a realistic MAC address for testing.
        
        Returns:
            MAC address string
        """
        # Use locally administered MAC address prefix (first byte has bit 1 set)
        mac_bytes = [0x02] + [random.randint(0x00, 0xff) for _ in range(5)]
        return ':'.join([f'{b:02x}' for b in mac_bytes])
    
    @staticmethod
    def is_mock_mode_enabled() -> bool:
        """
        Check if mock mode is enabled via environment variable.
        
        Returns:
            True if mock mode is enabled, False otherwise
        """
        return os.getenv('NETGRID_MOCK_MODE', '').lower() in ('1', 'true', 'yes', 'on')
    
    @staticmethod
    def get_mock_config() -> Dict[str, Any]:
        """
        Get mock configuration from environment variables.
        
        Returns:
            Dictionary with mock configuration options
        """
        return {
            'include_virtual': os.getenv('NETGRID_MOCK_INCLUDE_VIRTUAL', 'true').lower() in ('1', 'true', 'yes'),
            'include_filtered': os.getenv('NETGRID_MOCK_INCLUDE_FILTERED', 'false').lower() in ('1', 'true', 'yes'),
        }