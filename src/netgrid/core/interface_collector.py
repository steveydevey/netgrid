"""
Network interface collector module.

This module provides functionality to discover and collect information about
network interfaces from the system using various methods including system
tools, filesystem access, and system calls.
"""

import subprocess
import re
import json
import asyncio
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
        self._ip_config_cache: Dict[str, str] = {}  # Cache for IP configuration detection
        if enable_vendor_lookup:
            try:
                self._vendor_lookup = VendorLookup()
            except Exception as e:
                print(f"Warning: Vendor lookup disabled due to error: {e}")
                self._vendor_lookup = None
    
    def get_all_interfaces(self) -> InterfaceCollection:
        """
        Get all ethernet network interfaces from the system.
        
        Returns:
            InterfaceCollection containing all discovered ethernet interfaces
        """
        if self._interfaces_cache is None:
            self._interfaces_cache = asyncio.run(self._discover_interfaces_async())
        return self._interfaces_cache
    
    def refresh_interfaces(self) -> InterfaceCollection:
        """
        Refresh the interface cache and return updated information.
        
        Returns:
            InterfaceCollection containing refreshed interface data
        """
        self._interfaces_cache = None
        self._ip_config_cache.clear()  # Clear IP config cache on refresh
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
    
    def _detect_ip_config_type(self, interface_name: str) -> str:
        """
        Detect whether an interface uses DHCP or static IP configuration.
        
        Args:
            interface_name: Name of the interface to check
            
        Returns:
            "DHCP", "Static", or "Unknown"
        """
        # Check cache first
        if interface_name in self._ip_config_cache:
            return self._ip_config_cache[interface_name]
        
        # For virtual interfaces, return Unknown quickly
        if (interface_name.startswith(('veth', 'br-', 'docker', 'virbr')) or 
            interface_name == 'lo' or 
            interface_name.startswith('tailscale')):
            self._ip_config_cache[interface_name] = "Unknown"
            return "Unknown"
        
        # Quick check for active DHCP client processes (most reliable and fastest)
        if self._is_dhcp_client_running(interface_name):
            self._ip_config_cache[interface_name] = "DHCP"
            return "DHCP"
        
        # For physical interfaces, do a quick check of common configuration sources
        config_type = self._quick_config_check(interface_name)
        if config_type != "Unknown":
            self._ip_config_cache[interface_name] = config_type
            return config_type
        
        # Default to Unknown for performance
        self._ip_config_cache[interface_name] = "Unknown"
        return "Unknown"
    
    def _quick_config_check(self, interface_name: str) -> str:
        """
        Quick check of common configuration sources.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            "DHCP", "Static", or "Unknown"
        """
        try:
            # Check NetworkManager (most common on modern systems)
            result = subprocess.run(
                ["systemctl", "is-active", "NetworkManager"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0 and result.stdout.strip() == "active":
                # Quick NetworkManager check
                result = subprocess.run(
                    ["nmcli", "-t", "-f", "DEVICE,TYPE", "connection", "show", "--active"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip() and interface_name in line:
                            # Found the interface, check if it's DHCP
                            if 'ethernet' in line.lower():
                                # For ethernet, assume DHCP unless we can prove otherwise
                                return "DHCP"
            
            # Check systemd-networkd
            result = subprocess.run(
                ["systemctl", "is-active", "systemd-networkd"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0 and result.stdout.strip() == "active":
                # Quick systemd-networkd check
                result = subprocess.run(
                    ["networkctl", "status", interface_name],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    if "DHCP" in result.stdout:
                        return "DHCP"
                    elif "static" in result.stdout.lower():
                        return "Static"
                        
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return "Unknown"
    
    def _is_dhcp_client_running(self, interface_name: str) -> bool:
        """
        Check if a DHCP client is actively running for the interface.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            True if DHCP client is running for this interface
        """
        try:
            # Check for dhclient processes (fastest check)
            result = subprocess.run(
                ["pgrep", "-f", f"dhclient.*{interface_name}"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                return True
            
            # Check for systemd-networkd DHCP (quick check)
            result = subprocess.run(
                ["systemctl", "is-active", "systemd-networkd"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0 and result.stdout.strip() == "active":
                # Quick check if interface is managed by systemd-networkd with DHCP
                result = subprocess.run(
                    ["networkctl", "status", interface_name],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 and "DHCP" in result.stdout:
                    return True
            
            # Check for NetworkManager DHCP (quick check)
            result = subprocess.run(
                ["systemctl", "is-active", "NetworkManager"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0 and result.stdout.strip() == "active":
                result = subprocess.run(
                    ["nmcli", "-t", "-f", "DEVICE,TYPE", "device", "show", interface_name],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 and "dhcp" in result.stdout.lower():
                    return True
                    
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return False
    
    async def _discover_interfaces_async(self) -> InterfaceCollection:
        """
        Discover all network interfaces on the system using a single 'ip -j addr show' call.
        Returns:
            InterfaceCollection with all discovered interfaces
        """
        collection = InterfaceCollection()
        try:
            result = subprocess.run(["ip", "-j", "addr", "show"], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                print(f"Warning: Failed to run 'ip -j addr show': {result.stderr}")
                return collection
            ip_data = json.loads(result.stdout)
            for iface in ip_data:
                name = iface.get("ifname")
                mac_address = iface.get("address")
                ip_addresses = [addr["local"] for addr in iface.get("addr_info", []) if "local" in addr]
                # Determine state
                state = iface.get("operstate", "UNKNOWN").upper()
                is_up = state == "UP"
                link_state = LinkState.UP if is_up else LinkState.DOWN
                # MTU
                mtu = iface.get("mtu")
                # Flags
                flags = iface.get("flags", [])
                # Interface type (simple heuristic)
                if name == "lo":
                    interface_type = InterfaceType.LOOPBACK
                elif name.startswith(("veth", "br-", "docker", "virbr")):
                    interface_type = InterfaceType.VIRTUAL
                else:
                    interface_type = InterfaceType.PHYSICAL
                
                # Detect IP configuration type
                ip_config_type = self._detect_ip_config_type(name)
                
                # Build NetworkInterface
                ni = NetworkInterface(
                    name=name,
                    link_state=link_state,
                    speed=None,  # Will be filled by async ethtool lookup
                    mac_address=mac_address,
                    ip_addresses=ip_addresses,
                    mtu=mtu,
                    driver=None,
                    interface_type=interface_type,
                    vendor=None,
                    ip_config_type=ip_config_type,
                    description=None,
                    flags=flags,
                    duplex=None,  # Will be filled by async ethtool lookup
                    extra_data={},
                )
                collection.add_interface(ni)
        except Exception as e:
            print(f"Warning: Failed to collect interfaces: {e}")
        
        # Populate speed and duplex info asynchronously for physical interfaces
        await self._populate_ethtool_info_async(collection)
        
        # Populate vendor information in bulk if enabled
        if self._vendor_lookup:
            self._populate_vendors(collection)
        return collection
    
    async def _populate_ethtool_info_async(self, collection: InterfaceCollection) -> None:
        """
        Populate speed and duplex information for physical interfaces using async ethtool calls.
        
        Args:
            collection: InterfaceCollection to populate ethtool info for
        """
        physical_interfaces = [iface for iface in collection.interfaces 
                             if iface.interface_type == InterfaceType.PHYSICAL]
        
        if not physical_interfaces:
            return
        
        # Create tasks for all ethtool lookups
        tasks = []
        for interface in physical_interfaces:
            task = self._get_ethtool_info_async(interface.name)
            tasks.append((interface, task))
        
        # Run all ethtool lookups in parallel
        for interface, task in tasks:
            try:
                speed, duplex = await task
                interface.speed = speed
                interface.duplex = duplex
            except Exception as e:
                # Silently continue if ethtool fails for an interface
                pass
    
    async def _get_ethtool_info_async(self, interface_name: str) -> tuple[Optional[int], DuplexMode]:
        """
        Get speed and duplex information for an interface using ethtool.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            Tuple of (speed, duplex) where speed is in Mbps or None
        """
        try:
            # Run ethtool in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    ["ethtool", interface_name],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
            )
            
            if result.returncode != 0:
                return None, DuplexMode.UNKNOWN
            
            speed = None
            duplex = DuplexMode.UNKNOWN
            
            # Parse speed and duplex from ethtool output
            for line in result.stdout.split('\n'):
                if 'Speed:' in line:
                    match = re.search(r'Speed:\s*(\d+)\s*Mb/s', line)
                    if match:
                        speed = int(match.group(1))
                elif 'Duplex:' in line:
                    if 'Full' in line:
                        duplex = DuplexMode.FULL
                    elif 'Half' in line:
                        duplex = DuplexMode.HALF
            
            return speed, duplex
            
        except Exception:
            return None, DuplexMode.UNKNOWN
    
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
            # Perform bulk lookup (cache-first)
            vendor_results = self._vendor_lookup.bulk_lookup(mac_addresses)
            # Update interfaces with vendor information
            for interface in physical_interfaces:
                if interface.mac_address and interface.mac_address in vendor_results:
                    interface.vendor = vendor_results[interface.mac_address]
        except Exception as e:
            print(f"Warning: Failed to populate vendors: {e}")


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