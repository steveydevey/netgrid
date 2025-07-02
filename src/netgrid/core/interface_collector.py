"""
Network interface collector module.

This module provides functionality to discover and collect information about
network interfaces from the system using various methods including system
tools, filesystem access, and system calls.
"""

import os
import subprocess
import re
from typing import List, Dict, Optional, Any
from pathlib import Path

from .data_models import (
    NetworkInterface,
    InterfaceCollection,
    InterfaceType,
    LinkState,
    DuplexMode,
)
from .vendor_lookup import VendorLookup


class InterfaceCollector:
    """
    Collects network interface information from the system.
    
    This class provides methods to discover network interfaces and gather
    detailed information about each interface using system tools and
    filesystem access.
    """
    
    def __init__(self, enable_vendor_lookup: bool = True):
        """
        Initialize the interface collector.
        
        Args:
            enable_vendor_lookup: Whether to enable vendor lookup for MAC addresses
        """
        self._interfaces_cache: Optional[InterfaceCollection] = None
        self._vendor_lookup: Optional[VendorLookup] = None
        
        if enable_vendor_lookup:
            try:
                self._vendor_lookup = VendorLookup()
            except Exception as e:
                print(f"Warning: Vendor lookup disabled due to error: {e}")
                self._vendor_lookup = None
    
    def get_all_interfaces(self) -> InterfaceCollection:
        """
        Get all network interfaces from the system.
        
        Returns:
            InterfaceCollection containing all discovered interfaces
        """
        if self._interfaces_cache is None:
            self._interfaces_cache = self._discover_interfaces()
        return self._interfaces_cache
    
    def refresh_interfaces(self) -> InterfaceCollection:
        """
        Refresh the interface cache and return updated information.
        
        Returns:
            InterfaceCollection containing refreshed interface data
        """
        self._interfaces_cache = None
        return self.get_all_interfaces()
    
    def get_interface_details(self, interface_name: str) -> Optional[NetworkInterface]:
        """
        Get detailed information for a specific interface.
        
        Args:
            interface_name: Name of the interface to query
            
        Returns:
            NetworkInterface object if found, None otherwise
        """
        interfaces = self.get_all_interfaces()
        return interfaces.get_interface(interface_name)
    
    def _discover_interfaces(self) -> InterfaceCollection:
        """
        Discover all network interfaces on the system.
        
        Returns:
            InterfaceCollection with all discovered interfaces
        """
        collection = InterfaceCollection()
        
        # Get basic interface list from /sys/class/net
        interface_names = self._get_interface_names()
        
        for name in interface_names:
            try:
                interface = self._collect_interface_info(name)
                if interface:
                    collection.add_interface(interface)
            except Exception as e:
                # Log error but continue with other interfaces
                print(f"Warning: Failed to collect info for interface {name}: {e}")
        
        # Populate vendor information in bulk if enabled
        if self._vendor_lookup:
            self._populate_vendors(collection)
        
        return collection
    
    def _populate_vendors(self, collection: InterfaceCollection) -> None:
        """
        Populate vendor information for all interfaces in bulk.
        
        Args:
            collection: InterfaceCollection to populate vendors for
        """
        if not self._vendor_lookup:
            return
        
        # Collect MAC addresses only from physical interfaces
        mac_addresses = []
        physical_interfaces = []
        for interface in collection.interfaces:
            if (interface.mac_address and 
                interface.interface_type == InterfaceType.PHYSICAL and
                not interface.name.startswith(('veth', 'br-', 'docker', 'virbr'))):
                mac_addresses.append(interface.mac_address)
                physical_interfaces.append(interface)
        
        if not mac_addresses:
            return
        
        try:
            print(f"Looking up vendors for {len(mac_addresses)} physical interfaces...")
            # Perform bulk lookup
            vendor_results = self._vendor_lookup.bulk_lookup(mac_addresses)
            
            # Update interfaces with vendor information
            for interface in physical_interfaces:
                if interface.mac_address and interface.mac_address in vendor_results:
                    interface.vendor = vendor_results[interface.mac_address]
                    
        except Exception as e:
            print(f"Warning: Failed to populate vendors: {e}")
    
    def _get_interface_names(self) -> List[str]:
        """
        Get list of interface names from /sys/class/net.
        
        Returns:
            List of interface names
        """
        net_path = Path("/sys/class/net")
        if not net_path.exists():
            return []
        
        interfaces = []
        for item in net_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                interfaces.append(item.name)
        
        return sorted(interfaces)
    
    def _collect_interface_info(self, interface_name: str) -> Optional[NetworkInterface]:
        """
        Collect comprehensive information for a single interface.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            NetworkInterface object with collected information
        """
        # Basic interface information
        interface_type = self._determine_interface_type(interface_name)
        link_state = self._get_link_state(interface_name)
        mac_address = self._get_mac_address(interface_name)
        ip_addresses = self._get_ip_addresses(interface_name)
        mtu = self._get_mtu(interface_name)
        driver = self._get_driver(interface_name)
        
        # Advanced information (may require root privileges)
        speed = self._get_speed(interface_name)
        duplex = self._get_duplex(interface_name)
        description = self._get_description(interface_name)
        flags = self._get_flags(interface_name)
        
        # Vendor information (if enabled) - will be populated later in bulk
        vendor = None
        
        # Additional metadata
        extra_data = self._get_extra_data(interface_name)
        
        return NetworkInterface(
            name=interface_name,
            mac_address=mac_address,
            ip_addresses=ip_addresses,
            link_state=link_state,
            speed=speed,
            duplex=duplex,
            mtu=mtu,
            driver=driver,
            interface_type=interface_type,
            vendor=vendor,
            description=description,
            flags=flags,
            extra_data=extra_data
        )
    
    def _determine_interface_type(self, interface_name: str) -> InterfaceType:
        """
        Determine the type of network interface.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            InterfaceType enum value
        """
        # Check for loopback
        if interface_name == "lo":
            return InterfaceType.LOOPBACK
        
        # Check for virtual interfaces
        if interface_name.startswith(('veth', 'docker', 'br-', 'virbr')):
            return InterfaceType.VIRTUAL
        
        # Check for wireless interfaces
        if interface_name.startswith('wlan') or interface_name.startswith('wifi'):
            return InterfaceType.WIRELESS
        
        # Check for bridge interfaces
        if interface_name.startswith('br'):
            return InterfaceType.BRIDGE
        
        # Check for bond interfaces
        if interface_name.startswith('bond'):
            return InterfaceType.BOND
        
        # Check for VLAN interfaces
        if '.' in interface_name and interface_name.split('.')[1].isdigit():
            return InterfaceType.VLAN
        
        # Check if physical interface exists
        if self._is_physical_interface(interface_name):
            return InterfaceType.PHYSICAL
        
        return InterfaceType.UNKNOWN
    
    def _is_physical_interface(self, interface_name: str) -> bool:
        """
        Check if an interface is physical by looking for device files.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            True if physical interface, False otherwise
        """
        # Check for device file in /sys/class/net
        device_path = Path(f"/sys/class/net/{interface_name}/device")
        if device_path.exists():
            return True
        
        # Check for PCI device
        pci_path = Path(f"/sys/class/net/{interface_name}/device/uevent")
        if pci_path.exists():
            try:
                content = pci_path.read_text()
                if "PCI_ID" in content or "PCI_SLOT_NAME" in content:
                    return True
            except (OSError, IOError):
                pass
        
        return False
    
    def _get_link_state(self, interface_name: str) -> LinkState:
        """
        Get the current link state of an interface.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            LinkState enum value
        """
        try:
            # Read from /sys/class/net/{interface}/operstate
            operstate_path = Path(f"/sys/class/net/{interface_name}/operstate")
            if operstate_path.exists():
                state = operstate_path.read_text().strip().lower()
                if state == "up":
                    return LinkState.UP
                elif state == "down":
                    return LinkState.DOWN
            
            # Fallback: check if interface exists in /proc/net/dev
            proc_net_dev = Path("/proc/net/dev")
            if proc_net_dev.exists():
                content = proc_net_dev.read_text()
                if interface_name in content:
                    # If interface exists in proc, assume it's at least configured
                    return LinkState.DOWN
        except (OSError, IOError):
            pass
        
        return LinkState.UNKNOWN
    
    def _get_mac_address(self, interface_name: str) -> Optional[str]:
        """
        Get the MAC address of an interface.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            MAC address string or None if not found
        """
        try:
            # Read from /sys/class/net/{interface}/address
            address_path = Path(f"/sys/class/net/{interface_name}/address")
            if address_path.exists():
                mac = address_path.read_text().strip()
                if mac and mac != "00:00:00:00:00:00":
                    return mac
        except (OSError, IOError):
            pass
        
        return None
    
    def _get_ip_addresses(self, interface_name: str) -> List[str]:
        """
        Get IP addresses for an interface using ip command.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            List of IP addresses
        """
        addresses = []
        
        try:
            # Use ip command to get addresses
            result = subprocess.run(
                ["ip", "addr", "show", interface_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse output for inet and inet6 addresses
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line.startswith('inet '):
                        # IPv4 address
                        match = re.search(r'inet (\S+)', line)
                        if match:
                            addr = match.group(1).split('/')[0]  # Remove CIDR
                            addresses.append(addr)
                    elif line.startswith('inet6 '):
                        # IPv6 address
                        match = re.search(r'inet6 (\S+)', line)
                        if match:
                            addr = match.group(1).split('/')[0]  # Remove CIDR
                            addresses.append(addr)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return addresses
    
    def _get_mtu(self, interface_name: str) -> Optional[int]:
        """
        Get the MTU of an interface.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            MTU value or None if not found
        """
        try:
            # Read from /sys/class/net/{interface}/mtu
            mtu_path = Path(f"/sys/class/net/{interface_name}/mtu")
            if mtu_path.exists():
                mtu = int(mtu_path.read_text().strip())
                return mtu
        except (OSError, IOError, ValueError):
            pass
        
        return None
    
    def _get_driver(self, interface_name: str) -> Optional[str]:
        """
        Get the driver name for an interface.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            Driver name or None if not found
        """
        try:
            # Read from /sys/class/net/{interface}/device/driver/module/name
            driver_path = Path(f"/sys/class/net/{interface_name}/device/driver/module/name")
            if driver_path.exists():
                driver = driver_path.read_text().strip()
                return driver
            
            # Alternative: read from /sys/class/net/{interface}/device/driver
            driver_path = Path(f"/sys/class/net/{interface_name}/device/driver")
            if driver_path.exists():
                driver = driver_path.name
                return driver
        except (OSError, IOError):
            pass
        
        return None
    
    def _get_speed(self, interface_name: str) -> Optional[int]:
        """
        Get the current speed of an interface using ethtool.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            Speed in Mbps or None if not found
        """
        try:
            result = subprocess.run(
                ["ethtool", interface_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse speed from ethtool output
                for line in result.stdout.split('\n'):
                    if 'Speed:' in line:
                        match = re.search(r'Speed:\s*(\d+)\s*Mb/s', line)
                        if match:
                            return int(match.group(1))
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return None
    
    def _get_duplex(self, interface_name: str) -> DuplexMode:
        """
        Get the duplex mode of an interface using ethtool.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            DuplexMode enum value
        """
        try:
            result = subprocess.run(
                ["ethtool", interface_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse duplex from ethtool output
                for line in result.stdout.split('\n'):
                    if 'Duplex:' in line:
                        if 'Full' in line:
                            return DuplexMode.FULL
                        elif 'Half' in line:
                            return DuplexMode.HALF
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return DuplexMode.UNKNOWN
    
    def _get_description(self, interface_name: str) -> Optional[str]:
        """
        Get a description for the interface.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            Description string or None
        """
        # For now, return None. This could be enhanced with:
        # - Reading from udev rules
        # - Reading from systemd network configuration
        # - Reading from interface aliases
        return None
    
    def _get_flags(self, interface_name: str) -> List[str]:
        """
        Get interface flags.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            List of interface flags
        """
        flags = []
        
        try:
            # Read from /sys/class/net/{interface}/flags
            flags_path = Path(f"/sys/class/net/{interface_name}/flags")
            if flags_path.exists():
                flags_value = int(flags_path.read_text().strip(), 16)
                
                # Common interface flags
                if flags_value & 0x1:  # IFF_UP
                    flags.append("UP")
                if flags_value & 0x2:  # IFF_BROADCAST
                    flags.append("BROADCAST")
                if flags_value & 0x4:  # IFF_DEBUG
                    flags.append("DEBUG")
                if flags_value & 0x8:  # IFF_LOOPBACK
                    flags.append("LOOPBACK")
                if flags_value & 0x10:  # IFF_POINTOPOINT
                    flags.append("POINTOPOINT")
                if flags_value & 0x20:  # IFF_NOTRAILERS
                    flags.append("NOTRAILERS")
                if flags_value & 0x40:  # IFF_RUNNING
                    flags.append("RUNNING")
                if flags_value & 0x80:  # IFF_NOARP
                    flags.append("NOARP")
                if flags_value & 0x100:  # IFF_PROMISC
                    flags.append("PROMISC")
                if flags_value & 0x200:  # IFF_ALLMULTI
                    flags.append("ALLMULTI")
                if flags_value & 0x400:  # IFF_MASTER
                    flags.append("MASTER")
                if flags_value & 0x800:  # IFF_SLAVE
                    flags.append("SLAVE")
                if flags_value & 0x1000:  # IFF_MULTICAST
                    flags.append("MULTICAST")
                if flags_value & 0x2000:  # IFF_PORTSEL
                    flags.append("PORTSEL")
                if flags_value & 0x4000:  # IFF_AUTOMEDIA
                    flags.append("AUTOMEDIA")
                if flags_value & 0x8000:  # IFF_DYNAMIC
                    flags.append("DYNAMIC")
        except (OSError, IOError, ValueError):
            pass
        
        return flags
    
    def _get_extra_data(self, interface_name: str) -> Dict[str, Any]:
        """
        Get additional interface data.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            Dictionary of additional data
        """
        extra_data = {}
        
        try:
            # Get carrier status
            carrier_path = Path(f"/sys/class/net/{interface_name}/carrier")
            if carrier_path.exists():
                carrier = carrier_path.read_text().strip()
                extra_data["carrier"] = carrier
            
            # Get device type
            type_path = Path(f"/sys/class/net/{interface_name}/type")
            if type_path.exists():
                dev_type = type_path.read_text().strip()
                extra_data["device_type"] = dev_type
            
            # Get queue length
            tx_queue_len_path = Path(f"/sys/class/net/{interface_name}/tx_queue_len")
            if tx_queue_len_path.exists():
                tx_queue_len = tx_queue_len_path.read_text().strip()
                extra_data["tx_queue_len"] = tx_queue_len
        except (OSError, IOError):
            pass
        
        return extra_data


def get_all_interfaces() -> InterfaceCollection:
    """
    Convenience function to get all network interfaces.
    
    Returns:
        InterfaceCollection with all interfaces
    """
    collector = InterfaceCollector()
    return collector.get_all_interfaces()


def get_interface_details(interface_name: str) -> Optional[NetworkInterface]:
    """
    Convenience function to get details for a specific interface.
    
    Args:
        interface_name: Name of the interface
        
    Returns:
        NetworkInterface object if found, None otherwise
    """
    collector = InterfaceCollector()
    return collector.get_interface_details(interface_name) 