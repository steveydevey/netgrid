"""
Data models for network interface information.

This module defines the core data structures used throughout the NetGrid application
for representing network interface information.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class InterfaceType(Enum):
    """Enumeration of network interface types."""
    PHYSICAL = "physical"
    VIRTUAL = "virtual"
    LOOPBACK = "loopback"
    WIRELESS = "wireless"
    BRIDGE = "bridge"
    BOND = "bond"
    VLAN = "vlan"
    UNKNOWN = "unknown"


class LinkState(Enum):
    """Enumeration of network interface link states."""
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


class DuplexMode(Enum):
    """Enumeration of duplex modes."""
    FULL = "full"
    HALF = "half"
    UNKNOWN = "unknown"


@dataclass
class NetworkInterface:
    """
    Data class representing a network interface.
    
    This class contains all the information about a single network interface
    including its basic properties, addresses, and status information.
    """
    
    # Basic properties
    name: str
    mac_address: Optional[str] = None
    ip_addresses: List[str] = field(default_factory=list)
    
    # Status information
    link_state: LinkState = LinkState.UNKNOWN
    speed: Optional[int] = None  # Speed in Mbps
    duplex: DuplexMode = DuplexMode.UNKNOWN
    
    # Configuration
    mtu: Optional[int] = None
    driver: Optional[str] = None
    interface_type: InterfaceType = InterfaceType.UNKNOWN
    
    # Vendor information
    vendor: Optional[str] = None
    
    # IP configuration type (DHCP, Static, Unknown)
    ip_config_type: str = "Unknown"
    
    # Additional metadata
    description: Optional[str] = None
    flags: List[str] = field(default_factory=list)
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        if self.name is None or not self.name.strip():
            raise ValueError("Interface name cannot be empty")
        
        # Normalize MAC address format
        if self.mac_address:
            self.mac_address = self._normalize_mac_address(self.mac_address)
    
    def _normalize_mac_address(self, mac: str) -> str:
        """
        Normalize MAC address to standard format (XX:XX:XX:XX:XX:XX).
        
        Args:
            mac: MAC address in any common format
            
        Returns:
            Normalized MAC address string
        """
        if not mac:
            return mac
        
        # Remove common separators and convert to uppercase
        mac = mac.replace(':', '').replace('-', '').replace('.', '').upper()
        
        # Validate length
        if len(mac) != 12:
            raise ValueError(f"Invalid MAC address length: {mac}")
        
        # Add colons every 2 characters
        return ':'.join(mac[i:i+2] for i in range(0, 12, 2))
    
    @property
    def is_up(self) -> bool:
        """Check if the interface is up."""
        return self.link_state == LinkState.UP
    
    @property
    def is_physical(self) -> bool:
        """Check if this is a physical interface."""
        return self.interface_type == InterfaceType.PHYSICAL
    
    @property
    def has_ip(self) -> bool:
        """Check if the interface has any IP addresses."""
        return len(self.ip_addresses) > 0
    
    @property
    def primary_ip(self) -> Optional[str]:
        """Get the primary IP address (first IPv4, then first IPv6)."""
        if not self.ip_addresses:
            return None
        
        # Prefer IPv4 addresses
        ipv4_addresses = [ip for ip in self.ip_addresses if ':' not in ip]
        if ipv4_addresses:
            return ipv4_addresses[0]
        
        # Fall back to IPv6
        return self.ip_addresses[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the interface to a dictionary representation."""
        return {
            'name': self.name,
            'mac_address': self.mac_address,
            'ip_addresses': self.ip_addresses,
            'link_state': self.link_state.value,
            'speed': self.speed,
            'duplex': self.duplex.value,
            'mtu': self.mtu,
            'driver': self.driver,
            'interface_type': self.interface_type.value,
            'vendor': self.vendor,
            'ip_config_type': self.ip_config_type,
            'description': self.description,
            'flags': self.flags,
            'extra_data': self.extra_data,
        }
    
    def __str__(self) -> str:
        """String representation of the interface."""
        status = "UP" if self.is_up else "DOWN"
        ip_info = f" ({self.primary_ip})" if self.primary_ip else ""
        return f"{self.name}: {status}{ip_info}"


@dataclass
class InterfaceCollection:
    """
    Container for multiple network interfaces.
    
    This class provides methods for filtering, sorting, and searching
    through a collection of network interfaces.
    """
    
    interfaces: List[NetworkInterface] = field(default_factory=list)
    
    def add_interface(self, interface: NetworkInterface) -> None:
        """Add an interface to the collection."""
        self.interfaces.append(interface)
    
    def get_interface(self, name: str) -> Optional[NetworkInterface]:
        """Get an interface by name."""
        for interface in self.interfaces:
            if interface.name == name:
                return interface
        return None
    
    def filter_by_state(self, state: LinkState) -> 'InterfaceCollection':
        """Filter interfaces by link state."""
        filtered = [iface for iface in self.interfaces if iface.link_state == state]
        return InterfaceCollection(filtered)
    
    def filter_by_type(self, interface_type: InterfaceType) -> 'InterfaceCollection':
        """Filter interfaces by type."""
        filtered = [iface for iface in self.interfaces if iface.interface_type == interface_type]
        return InterfaceCollection(filtered)
    
    def filter_up(self) -> 'InterfaceCollection':
        """Get only interfaces that are up."""
        return self.filter_by_state(LinkState.UP)
    
    def filter_down(self) -> 'InterfaceCollection':
        """Get only interfaces that are down."""
        return self.filter_by_state(LinkState.DOWN)
    
    def filter_physical(self) -> 'InterfaceCollection':
        """Get only physical interfaces."""
        return self.filter_by_type(InterfaceType.PHYSICAL)
    
    def sort_by_name(self, reverse: bool = False) -> 'InterfaceCollection':
        """Sort interfaces by name."""
        sorted_interfaces = sorted(self.interfaces, key=lambda x: x.name, reverse=reverse)
        return InterfaceCollection(sorted_interfaces)
    
    def sort_by_state(self, reverse: bool = False) -> 'InterfaceCollection':
        """Sort interfaces by state (up interfaces first by default)."""
        def state_priority(iface):
            # Lower value = higher priority
            if iface.link_state == LinkState.UP:
                return 0
            elif iface.link_state == LinkState.DOWN:
                return 1
            else:
                return 2
        sorted_interfaces = sorted(
            self.interfaces,
            key=lambda x: (state_priority(x), x.name),
            reverse=reverse
        )
        return InterfaceCollection(sorted_interfaces)
    
    def __len__(self) -> int:
        """Return the number of interfaces in the collection."""
        return len(self.interfaces)
    
    def __iter__(self):
        """Iterate over interfaces."""
        return iter(self.interfaces)
    
    def __getitem__(self, index):
        """Get interface by index."""
        return self.interfaces[index]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the collection to a dictionary representation."""
        return {
            'interfaces': [iface.to_dict() for iface in self.interfaces],
            'count': len(self.interfaces),
            'up_count': len(self.filter_up()),
            'down_count': len(self.filter_down()),
        } 