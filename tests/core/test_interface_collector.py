"""
Tests for the InterfaceCollector module.

These tests verify that the InterfaceCollector can discover interfaces and collect
basic information from the system. They do not require any text files and will skip
tests gracefully if no interfaces are found.
"""

import pytest
from netgrid.core.interface_collector import InterfaceCollector, get_all_interfaces, get_interface_details
from netgrid.core.data_models import LinkState, InterfaceType


def test_discover_interfaces():
    collector = InterfaceCollector()
    interfaces = collector.get_all_interfaces()
    assert len(interfaces) > 0, "No network interfaces found on this system."

    # At least one interface should have a name
    names = [iface.name for iface in interfaces]
    assert all(isinstance(n, str) and n for n in names)


def test_interface_fields():
    collector = InterfaceCollector()
    interfaces = collector.get_all_interfaces()
    if not interfaces:
        pytest.skip("No interfaces found to test fields.")
    iface = interfaces[0]
    assert iface.name
    assert iface.link_state in (LinkState.UP, LinkState.DOWN, LinkState.UNKNOWN)
    assert iface.interface_type in InterfaceType
    # MAC address may be None for some virtual interfaces, but should be a string if present
    if iface.mac_address:
        assert isinstance(iface.mac_address, str)
    # IP addresses is always a list
    assert isinstance(iface.ip_addresses, list)


def test_get_interface_details():
    collector = InterfaceCollector()
    interfaces = collector.get_all_interfaces()
    if not interfaces:
        pytest.skip("No interfaces found to test get_interface_details.")
    iface = interfaces[0]
    details = collector.get_interface_details(iface.name)
    assert details is not None
    assert details.name == iface.name


def test_convenience_functions():
    interfaces = get_all_interfaces()
    assert len(interfaces) > 0
    iface = interfaces[0]
    details = get_interface_details(iface.name)
    assert details is not None
    assert details.name == iface.name 