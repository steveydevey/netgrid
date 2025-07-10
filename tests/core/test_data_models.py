"""
Unit tests for the data models module.

This module tests the NetworkInterface and InterfaceCollection classes
and their associated enums and functionality.
"""

import pytest
from netgrid.core.data_models import (
    NetworkInterface,
    InterfaceCollection,
    InterfaceType,
    LinkState,
    DuplexMode,
)


class TestNetworkInterface:
    """Test cases for the NetworkInterface class."""
    
    def test_basic_interface_creation(self):
        """Test creating a basic network interface."""
        interface = NetworkInterface(name="eth0")
        
        assert interface.name == "eth0"
        assert interface.mac_address is None
        assert interface.ip_addresses == []
        assert interface.link_state == LinkState.UNKNOWN
        assert interface.is_up is False
    
    def test_interface_with_all_properties(self):
        """Test creating an interface with all properties set."""
        interface = NetworkInterface(
            name="eth0",
            mac_address="00:11:22:33:44:55",
            ip_addresses=["192.168.1.100", "2001:db8::1"],
            link_state=LinkState.UP,
            speed=1000,
            duplex=DuplexMode.FULL,
            mtu=1500,
            driver="e1000e",
            interface_type=InterfaceType.PHYSICAL,
            vendor="Intel Corporation",
            description="Ethernet interface"
        )
        
        assert interface.name == "eth0"
        assert interface.mac_address == "00:11:22:33:44:55"
        assert interface.ip_addresses == ["192.168.1.100", "2001:db8::1"]
        assert interface.link_state == LinkState.UP
        assert interface.speed == 1000
        assert interface.duplex == DuplexMode.FULL
        assert interface.mtu == 1500
        assert interface.driver == "e1000e"
        assert interface.interface_type == InterfaceType.PHYSICAL
        assert interface.vendor == "Intel Corporation"
        assert interface.description == "Ethernet interface"
        assert interface.is_up is True
        assert interface.is_physical is True
        assert interface.has_ip is True
    
    def test_mac_address_normalization(self):
        """Test MAC address normalization."""
        # Test with colons
        interface1 = NetworkInterface(name="eth0", mac_address="00:11:22:33:44:55")
        assert interface1.mac_address == "00:11:22:33:44:55"
        
        # Test with dashes
        interface2 = NetworkInterface(name="eth1", mac_address="00-11-22-33-44-55")
        assert interface2.mac_address == "00:11:22:33:44:55"
        
        # Test with dots
        interface3 = NetworkInterface(name="eth2", mac_address="0011.2233.4455")
        assert interface3.mac_address == "00:11:22:33:44:55"
        
        # Test without separators
        interface4 = NetworkInterface(name="eth3", mac_address="001122334455")
        assert interface4.mac_address == "00:11:22:33:44:55"
        
        # Test mixed case
        interface5 = NetworkInterface(name="eth4", mac_address="00:11:22:33:44:55")
        assert interface5.mac_address == "00:11:22:33:44:55"
    
    def test_invalid_mac_address(self):
        """Test that invalid MAC addresses raise ValueError."""
        with pytest.raises(ValueError, match="Invalid MAC address length"):
            NetworkInterface(name="eth0", mac_address="00:11:22:33:44")
    
    def test_empty_interface_name(self):
        """Test that empty interface names raise ValueError."""
        with pytest.raises(ValueError, match="Interface name cannot be empty"):
            NetworkInterface(name="")
        
        with pytest.raises(ValueError, match="Interface name cannot be empty"):
            NetworkInterface(name=None)
    
    def test_primary_ip_property(self):
        """Test the primary_ip property."""
        # Test with IPv4 only
        interface1 = NetworkInterface(name="eth0", ip_addresses=["192.168.1.100"])
        assert interface1.primary_ip == "192.168.1.100"
        
        # Test with IPv6 only
        interface2 = NetworkInterface(name="eth1", ip_addresses=["2001:db8::1"])
        assert interface2.primary_ip == "2001:db8::1"
        
        # Test with both IPv4 and IPv6 (should prefer IPv4)
        interface3 = NetworkInterface(
            name="eth2", 
            ip_addresses=["2001:db8::1", "192.168.1.100", "2001:db8::2"]
        )
        assert interface3.primary_ip == "192.168.1.100"
        
        # Test with no IP addresses
        interface4 = NetworkInterface(name="eth3")
        assert interface4.primary_ip is None
    
    def test_to_dict_method(self):
        """Test the to_dict method."""
        interface = NetworkInterface(
            name="eth0",
            mac_address="00:11:22:33:44:55",
            ip_addresses=["192.168.1.100"],
            link_state=LinkState.UP,
            speed=1000,
            duplex=DuplexMode.FULL,
            mtu=1500,
            driver="e1000e",
            interface_type=InterfaceType.PHYSICAL,
            vendor="Intel Corporation",
            description="Ethernet interface",
            flags=["UP", "BROADCAST"],
            extra_data={"custom_field": "custom_value"}
        )
        
        result = interface.to_dict()
        
        assert result["name"] == "eth0"
        assert result["mac_address"] == "00:11:22:33:44:55"
        assert result["ip_addresses"] == ["192.168.1.100"]
        assert result["link_state"] == "up"
        assert result["speed"] == 1000
        assert result["duplex"] == "full"
        assert result["mtu"] == 1500
        assert result["driver"] == "e1000e"
        assert result["interface_type"] == "physical"
        assert result["vendor"] == "Intel Corporation"
        assert result["description"] == "Ethernet interface"
        assert result["flags"] == ["UP", "BROADCAST"]
        assert result["extra_data"] == {"custom_field": "custom_value"}
    
    def test_string_representation(self):
        """Test the string representation of an interface."""
        # Interface with IP
        interface1 = NetworkInterface(
            name="eth0",
            link_state=LinkState.UP,
            ip_addresses=["192.168.1.100"]
        )
        assert str(interface1) == "eth0: UP (192.168.1.100)"
        
        # Interface without IP
        interface2 = NetworkInterface(
            name="eth1",
            link_state=LinkState.DOWN
        )
        assert str(interface2) == "eth1: DOWN"

    def test_network_interface_ip_config_type(self):
        iface = NetworkInterface(name='eth0', ip_config_type='DHCP')
        assert iface.ip_config_type == 'DHCP'
        iface2 = NetworkInterface(name='eth1')
        assert iface2.ip_config_type == 'Unknown'


class TestInterfaceCollection:
    """Test cases for the InterfaceCollection class."""
    
    def test_empty_collection(self):
        """Test creating an empty collection."""
        collection = InterfaceCollection()
        assert len(collection) == 0
        assert list(collection) == []
    
    def test_adding_interfaces(self):
        """Test adding interfaces to the collection."""
        collection = InterfaceCollection()
        
        interface1 = NetworkInterface(name="eth0", link_state=LinkState.UP)
        interface2 = NetworkInterface(name="eth1", link_state=LinkState.DOWN)
        
        collection.add_interface(interface1)
        collection.add_interface(interface2)
        
        assert len(collection) == 2
        assert collection[0].name == "eth0"
        assert collection[1].name == "eth1"
    
    def test_get_interface_by_name(self):
        """Test getting an interface by name."""
        collection = InterfaceCollection()
        
        interface1 = NetworkInterface(name="eth0")
        interface2 = NetworkInterface(name="eth1")
        
        collection.add_interface(interface1)
        collection.add_interface(interface2)
        
        assert collection.get_interface("eth0") == interface1
        assert collection.get_interface("eth1") == interface2
        assert collection.get_interface("nonexistent") is None
    
    def test_filter_by_state(self):
        """Test filtering interfaces by state."""
        collection = InterfaceCollection()
        
        up_interface = NetworkInterface(name="eth0", link_state=LinkState.UP)
        down_interface = NetworkInterface(name="eth1", link_state=LinkState.DOWN)
        
        collection.add_interface(up_interface)
        collection.add_interface(down_interface)
        
        up_interfaces = collection.filter_by_state(LinkState.UP)
        down_interfaces = collection.filter_by_state(LinkState.DOWN)
        
        assert len(up_interfaces) == 1
        assert up_interfaces[0].name == "eth0"
        
        assert len(down_interfaces) == 1
        assert down_interfaces[0].name == "eth1"
    
    def test_filter_by_type(self):
        """Test filtering interfaces by type."""
        collection = InterfaceCollection()
        
        physical_interface = NetworkInterface(
            name="eth0", 
            interface_type=InterfaceType.PHYSICAL
        )
        virtual_interface = NetworkInterface(
            name="veth0", 
            interface_type=InterfaceType.VIRTUAL
        )
        
        collection.add_interface(physical_interface)
        collection.add_interface(virtual_interface)
        
        physical_interfaces = collection.filter_by_type(InterfaceType.PHYSICAL)
        virtual_interfaces = collection.filter_by_type(InterfaceType.VIRTUAL)
        
        assert len(physical_interfaces) == 1
        assert physical_interfaces[0].name == "eth0"
        
        assert len(virtual_interfaces) == 1
        assert virtual_interfaces[0].name == "veth0"
    
    def test_filter_up_and_down(self):
        """Test the convenience filter methods."""
        collection = InterfaceCollection()
        
        up_interface = NetworkInterface(name="eth0", link_state=LinkState.UP)
        down_interface = NetworkInterface(name="eth1", link_state=LinkState.DOWN)
        
        collection.add_interface(up_interface)
        collection.add_interface(down_interface)
        
        up_interfaces = collection.filter_up()
        down_interfaces = collection.filter_down()
        
        assert len(up_interfaces) == 1
        assert up_interfaces[0].name == "eth0"
        
        assert len(down_interfaces) == 1
        assert down_interfaces[0].name == "eth1"
    
    def test_sort_by_name(self):
        """Test sorting interfaces by name."""
        collection = InterfaceCollection()
        
        interface2 = NetworkInterface(name="eth2")
        interface1 = NetworkInterface(name="eth1")
        interface3 = NetworkInterface(name="eth3")
        
        collection.add_interface(interface2)
        collection.add_interface(interface1)
        collection.add_interface(interface3)
        
        sorted_collection = collection.sort_by_name()
        
        assert sorted_collection[0].name == "eth1"
        assert sorted_collection[1].name == "eth2"
        assert sorted_collection[2].name == "eth3"
        
        # Test reverse sorting
        reverse_sorted = collection.sort_by_name(reverse=True)
        assert reverse_sorted[0].name == "eth3"
        assert reverse_sorted[1].name == "eth2"
        assert reverse_sorted[2].name == "eth1"
    
    def test_sort_by_state(self):
        """Test sorting interfaces by state."""
        collection = InterfaceCollection()
        
        down_interface = NetworkInterface(name="eth1", link_state=LinkState.DOWN)
        up_interface = NetworkInterface(name="eth0", link_state=LinkState.UP)
        
        collection.add_interface(down_interface)
        collection.add_interface(up_interface)
        
        sorted_collection = collection.sort_by_state()
        
        # Up interfaces should come first
        assert sorted_collection[0].name == "eth0"
        assert sorted_collection[1].name == "eth1"
    
    def test_to_dict_method(self):
        """Test the to_dict method."""
        collection = InterfaceCollection()
        
        up_interface = NetworkInterface(name="eth0", link_state=LinkState.UP)
        down_interface = NetworkInterface(name="eth1", link_state=LinkState.DOWN)
        
        collection.add_interface(up_interface)
        collection.add_interface(down_interface)
        
        result = collection.to_dict()
        
        assert result["count"] == 2
        assert result["up_count"] == 1
        assert result["down_count"] == 1
        assert len(result["interfaces"]) == 2
        assert result["interfaces"][0]["name"] == "eth0"
        assert result["interfaces"][1]["name"] == "eth1"


class TestEnums:
    """Test cases for the enum classes."""
    
    def test_interface_type_enum(self):
        """Test the InterfaceType enum."""
        assert InterfaceType.PHYSICAL.value == "physical"
        assert InterfaceType.VIRTUAL.value == "virtual"
        assert InterfaceType.LOOPBACK.value == "loopback"
        assert InterfaceType.WIRELESS.value == "wireless"
        assert InterfaceType.BRIDGE.value == "bridge"
        assert InterfaceType.BOND.value == "bond"
        assert InterfaceType.VLAN.value == "vlan"
        assert InterfaceType.UNKNOWN.value == "unknown"
    
    def test_link_state_enum(self):
        """Test the LinkState enum."""
        assert LinkState.UP.value == "up"
        assert LinkState.DOWN.value == "down"
        assert LinkState.UNKNOWN.value == "unknown"
    
    def test_duplex_mode_enum(self):
        """Test the DuplexMode enum."""
        assert DuplexMode.FULL.value == "full"
        assert DuplexMode.HALF.value == "half"
        assert DuplexMode.UNKNOWN.value == "unknown" 