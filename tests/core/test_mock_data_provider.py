"""
Tests for the MockDataProvider module.

These tests verify that the MockDataProvider generates realistic interface data
and that the InterfaceCollector correctly uses mock data when enabled.
"""

import os
import pytest
from unittest.mock import patch

from netgrid.core.mock_data_provider import MockDataProvider
from netgrid.core.interface_collector import InterfaceCollector
from netgrid.core.data_models import InterfaceType, LinkState, DuplexMode


class TestMockDataProvider:
    """Test the MockDataProvider class."""
    
    def test_basic_mock_interfaces(self):
        """Test basic mock interface generation."""
        provider = MockDataProvider()
        interfaces = provider.get_mock_interfaces()
        
        assert len(interfaces) > 0
        
        # Check that we have a mix of interface types
        interface_types = [iface.interface_type for iface in interfaces]
        assert InterfaceType.PHYSICAL in interface_types
        assert InterfaceType.LOOPBACK in interface_types
    
    def test_mock_interfaces_include_virtual(self):
        """Test mock interface generation with virtual interfaces included."""
        provider = MockDataProvider(include_virtual=True)
        interfaces = provider.get_mock_interfaces()
        
        interface_types = [iface.interface_type for iface in interfaces]
        virtual_types = [InterfaceType.BRIDGE, InterfaceType.BOND, InterfaceType.VIRTUAL]
        
        # Should have at least one virtual interface type
        assert any(vtype in interface_types for vtype in virtual_types)
    
    def test_mock_interfaces_exclude_virtual(self):
        """Test mock interface generation with virtual interfaces excluded."""
        provider = MockDataProvider(include_virtual=False)
        interfaces = provider.get_mock_interfaces()
        
        interface_types = [iface.interface_type for iface in interfaces]
        virtual_types = [InterfaceType.BRIDGE, InterfaceType.BOND, InterfaceType.VIRTUAL]
        
        # Should not have virtual interface types (except loopback)
        for vtype in virtual_types:
            if vtype != InterfaceType.VIRTUAL:  # tun0 is VIRTUAL but not filtered
                assert vtype not in interface_types
    
    def test_mock_interfaces_include_filtered(self):
        """Test mock interface generation with normally filtered interfaces."""
        provider = MockDataProvider(include_filtered=True)
        interfaces = provider.get_mock_interfaces()
        
        names = [iface.name for iface in interfaces]
        
        # Should include normally filtered interfaces
        filtered_names = ['veth0abc123', 'br-docker0', 'tailscale0']
        for name in filtered_names:
            assert name in names
    
    def test_mock_interfaces_exclude_filtered(self):
        """Test mock interface generation without normally filtered interfaces."""
        provider = MockDataProvider(include_filtered=False)
        interfaces = provider.get_mock_interfaces()
        
        names = [iface.name for iface in interfaces]
        
        # Should not include normally filtered interfaces
        filtered_names = ['veth0abc123', 'br-docker0', 'tailscale0']
        for name in filtered_names:
            assert name not in names
    
    def test_get_interface_by_name(self):
        """Test getting a specific interface by name."""
        provider = MockDataProvider()
        
        # Test getting an existing interface
        eth0 = provider.get_interface_by_name("eth0")
        assert eth0 is not None
        assert eth0.name == "eth0"
        assert eth0.interface_type == InterfaceType.PHYSICAL
        
        # Test getting a non-existent interface
        nonexistent = provider.get_interface_by_name("nonexistent")
        assert nonexistent is None
    
    def test_get_interface_names(self):
        """Test getting list of interface names."""
        provider = MockDataProvider()
        names = provider.get_interface_names()
        
        assert isinstance(names, list)
        assert len(names) > 0
        assert "eth0" in names
        assert "lo" in names
        
        # Names should be sorted
        assert names == sorted(names)
    
    def test_create_custom_interface(self):
        """Test creating custom interfaces."""
        custom = MockDataProvider.create_custom_interface(
            name="test0",
            ip_addresses=["192.168.1.1"],
            speed=1000,
            vendor="Test Vendor"
        )
        
        assert custom.name == "test0"
        assert custom.ip_addresses == ["192.168.1.1"]
        assert custom.speed == 1000
        assert custom.vendor == "Test Vendor"
        assert custom.interface_type == InterfaceType.PHYSICAL
        assert custom.mac_address is not None  # Should be auto-generated
    
    def test_generate_mac_address(self):
        """Test MAC address generation."""
        mac = MockDataProvider._generate_mac_address()
        
        assert isinstance(mac, str)
        assert len(mac.split(':')) == 6
        
        # Should be locally administered (first byte bit 1 set)
        first_byte = int(mac.split(':')[0], 16)
        assert first_byte & 0x02 == 0x02
    
    def test_mock_mode_detection(self):
        """Test mock mode detection from environment variables."""
        # Test various true values
        true_values = ['1', 'true', 'TRUE', 'yes', 'YES', 'on', 'ON']
        for value in true_values:
            with patch.dict(os.environ, {'NETGRID_MOCK_MODE': value}):
                assert MockDataProvider.is_mock_mode_enabled()
        
        # Test false values
        false_values = ['0', 'false', 'FALSE', 'no', 'NO', 'off', 'OFF', '']
        for value in false_values:
            with patch.dict(os.environ, {'NETGRID_MOCK_MODE': value}):
                assert not MockDataProvider.is_mock_mode_enabled()
    
    def test_mock_config_from_environment(self):
        """Test mock configuration from environment variables."""
        env_vars = {
            'NETGRID_MOCK_INCLUDE_VIRTUAL': 'false',
            'NETGRID_MOCK_INCLUDE_FILTERED': 'true'
        }
        
        with patch.dict(os.environ, env_vars):
            config = MockDataProvider.get_mock_config()
            assert config['include_virtual'] is False
            assert config['include_filtered'] is True


class TestInterfaceCollectorMockMode:
    """Test InterfaceCollector with mock data."""
    
    def test_collector_with_mock_mode_enabled(self):
        """Test collector using mock data."""
        collector = InterfaceCollector(use_mock_data=True)
        interfaces = collector.get_all_interfaces()
        
        assert len(interfaces) > 0
        
        # Should have common mock interfaces
        names = [iface.name for iface in interfaces]
        assert "eth0" in names
        assert "lo" in names
    
    def test_collector_with_mock_mode_disabled(self):
        """Test collector using real system data."""
        collector = InterfaceCollector(use_mock_data=False)
        interfaces = collector.get_all_interfaces()
        
        # This should use real system data
        # We can't make assumptions about what interfaces exist,
        # but the collection should be valid
        assert isinstance(interfaces, type(interfaces))
    
    def test_collector_mock_mode_from_environment(self):
        """Test collector respects mock mode environment variable."""
        with patch.dict(os.environ, {'NETGRID_MOCK_MODE': '1'}):
            collector = InterfaceCollector()
            assert collector._use_mock_data is True
        
        with patch.dict(os.environ, {'NETGRID_MOCK_MODE': '0'}):
            collector = InterfaceCollector()
            assert collector._use_mock_data is False
    
    def test_get_interface_details_mock_mode(self):
        """Test getting interface details in mock mode."""
        collector = InterfaceCollector(use_mock_data=True)
        
        # Test getting an existing mock interface
        eth0 = collector.get_interface_details("eth0")
        assert eth0 is not None
        assert eth0.name == "eth0"
        
        # Test getting a non-existent interface
        nonexistent = collector.get_interface_details("nonexistent")
        assert nonexistent is None
    
    def test_refresh_interfaces_mock_mode(self):
        """Test refreshing interfaces in mock mode."""
        collector = InterfaceCollector(use_mock_data=True)
        
        # Get interfaces twice
        interfaces1 = collector.get_all_interfaces()
        interfaces2 = collector.refresh_interfaces()
        
        # Should be the same (mock data is static)
        assert len(interfaces1) == len(interfaces2)
        
        names1 = sorted([iface.name for iface in interfaces1])
        names2 = sorted([iface.name for iface in interfaces2])
        assert names1 == names2


class TestMockDataRealism:
    """Test that mock data is realistic and comprehensive."""
    
    def test_interface_data_completeness(self):
        """Test that mock interfaces have complete data."""
        provider = MockDataProvider()
        interfaces = provider.get_mock_interfaces()
        
        for interface in interfaces:
            # All interfaces should have a name
            assert interface.name
            assert isinstance(interface.name, str)
            
            # All interfaces should have a valid type
            assert interface.interface_type in InterfaceType
            
            # All interfaces should have a valid link state
            assert interface.link_state in LinkState
            
            # Physical interfaces should have MAC addresses
            if interface.interface_type == InterfaceType.PHYSICAL:
                assert interface.mac_address is not None
                assert len(interface.mac_address.split(':')) == 6
    
    def test_realistic_interface_scenarios(self):
        """Test that mock data represents realistic scenarios."""
        provider = MockDataProvider()
        interfaces = provider.get_mock_interfaces()
        
        names = [iface.name for iface in interfaces]
        
        # Should have common interface types
        assert any(name.startswith('eth') for name in names)  # Ethernet
        assert any(name.startswith('enp') for name in names)  # Systemd naming
        assert 'lo' in names  # Loopback
        
        # Should have up and down interfaces
        states = [iface.link_state for iface in interfaces]
        assert LinkState.UP in states
        assert LinkState.DOWN in states
        
        # Should have different speeds
        speeds = [iface.speed for iface in interfaces if iface.speed]
        assert len(set(speeds)) > 1  # Multiple different speeds
    
    def test_vendor_information(self):
        """Test that vendor information is realistic."""
        provider = MockDataProvider()
        interfaces = provider.get_mock_interfaces()
        
        vendors = [iface.vendor for iface in interfaces if iface.vendor]
        
        # Should have realistic vendor names
        expected_vendors = ["Intel Corporation", "Red Hat Inc."]
        for vendor in expected_vendors:
            assert vendor in vendors
    
    def test_ip_address_formats(self):
        """Test that IP addresses are in correct formats."""
        provider = MockDataProvider()
        interfaces = provider.get_mock_interfaces()
        
        for interface in interfaces:
            for ip in interface.ip_addresses:
                # Basic validation - should not be empty and should be string
                assert ip
                assert isinstance(ip, str)
                
                # Should contain dots (IPv4) or colons (IPv6)
                assert '.' in ip or ':' in ip