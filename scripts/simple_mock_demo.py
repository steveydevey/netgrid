#!/usr/bin/env python3
"""
Simplified demo for NetGrid mock mode functionality.

This demo shows the mock data provider without requiring all dependencies.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import netgrid
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from netgrid.core.data_models import InterfaceType, LinkState
from netgrid.core.mock_data_provider import MockDataProvider


def demo_basic_mock_interfaces():
    """Show basic mock interface generation."""
    print("=== Basic Mock Interfaces ===")
    provider = MockDataProvider()
    interfaces = provider.get_mock_interfaces()
    
    print(f"Generated {len(interfaces)} mock interfaces:")
    print(f"{'Interface':<12} {'Type':<10} {'State':<6} {'Speed':<8} {'IP Address':<15} {'Vendor'}")
    print("-" * 80)
    
    for interface in interfaces:
        itype = interface.interface_type.value
        state = interface.link_state.value.upper()
        speed = f"{interface.speed}" if interface.speed else "N/A"
        ip = interface.primary_ip or "N/A"
        vendor = interface.vendor or "N/A"
        print(f"{interface.name:<12} {itype:<10} {state:<6} {speed:<8} {ip:<15} {vendor}")
    print()


def demo_configuration_options():
    """Show different configuration options."""
    print("=== Configuration Options ===")
    
    # Default configuration
    print("1. Default configuration:")
    provider = MockDataProvider()
    interfaces = provider.get_mock_interfaces()
    print(f"   {len(interfaces)} interfaces")
    
    # Include filtered interfaces
    print("2. Include filtered interfaces (veth, br-, tailscale):")
    provider = MockDataProvider(include_filtered=True)
    interfaces = provider.get_mock_interfaces()
    print(f"   {len(interfaces)} interfaces")
    filtered_names = [i.name for i in interfaces if i.name.startswith(('veth', 'br-', 'tailscale'))]
    print(f"   Filtered: {', '.join(filtered_names)}")
    
    # Exclude virtual interfaces
    print("3. Exclude virtual interfaces:")
    provider = MockDataProvider(include_virtual=False)
    interfaces = provider.get_mock_interfaces()
    print(f"   {len(interfaces)} interfaces")
    physical_names = [i.name for i in interfaces if i.interface_type in [InterfaceType.PHYSICAL, InterfaceType.WIRELESS]]
    print(f"   Physical: {', '.join(physical_names)}")
    print()


def demo_environment_variables():
    """Show environment variable usage."""
    print("=== Environment Variables ===")
    
    # Test different values
    test_values = ['1', 'true', 'yes', 'on', '0', 'false', 'no', 'off']
    
    print("Testing NETGRID_MOCK_MODE values:")
    for value in test_values:
        os.environ['NETGRID_MOCK_MODE'] = value
        enabled = MockDataProvider.is_mock_mode_enabled()
        print(f"   NETGRID_MOCK_MODE='{value}' -> {enabled}")
    
    # Clean up
    if 'NETGRID_MOCK_MODE' in os.environ:
        del os.environ['NETGRID_MOCK_MODE']
    
    print()
    print("Configuration from environment:")
    os.environ['NETGRID_MOCK_INCLUDE_VIRTUAL'] = 'false'
    os.environ['NETGRID_MOCK_INCLUDE_FILTERED'] = 'true'
    
    config = MockDataProvider.get_mock_config()
    print(f"   include_virtual: {config['include_virtual']}")
    print(f"   include_filtered: {config['include_filtered']}")
    
    # Clean up
    del os.environ['NETGRID_MOCK_INCLUDE_VIRTUAL']
    del os.environ['NETGRID_MOCK_INCLUDE_FILTERED']
    print()


def demo_custom_interfaces():
    """Show custom interface creation."""
    print("=== Custom Interface Creation ===")
    
    # Create various custom interfaces
    custom_interfaces = [
        MockDataProvider.create_custom_interface(
            name="custom-eth0",
            ip_addresses=["10.0.0.100", "fe80::1"],
            speed=10000,
            vendor="Custom Corp"
        ),
        MockDataProvider.create_custom_interface(
            name="test-wifi",
            interface_type=InterfaceType.WIRELESS,
            ip_addresses=["192.168.1.50"],
            speed=300,
            vendor="WiFi Inc"
        ),
        MockDataProvider.create_custom_interface(
            name="down-interface",
            link_state=LinkState.DOWN,
            speed=None
        )
    ]
    
    print("Created custom interfaces:")
    for interface in custom_interfaces:
        state = interface.link_state.value.upper()
        speed = f"{interface.speed} Mbps" if interface.speed else "N/A"
        ips = ", ".join(interface.ip_addresses) if interface.ip_addresses else "None"
        print(f"   {interface.name}: {state}, {speed}, IPs: {ips}")
    print()


def demo_realistic_data():
    """Show that mock data is realistic."""
    print("=== Realistic Mock Data ===")
    
    provider = MockDataProvider()
    interfaces = provider.get_mock_interfaces()
    
    # Analyze the data
    types = {}
    states = {}
    speeds = []
    vendors = set()
    
    for interface in interfaces:
        # Count types
        itype = interface.interface_type.value
        types[itype] = types.get(itype, 0) + 1
        
        # Count states
        state = interface.link_state.value
        states[state] = states.get(state, 0) + 1
        
        # Collect speeds
        if interface.speed:
            speeds.append(interface.speed)
        
        # Collect vendors
        if interface.vendor:
            vendors.add(interface.vendor)
    
    print(f"Interface types: {dict(types)}")
    print(f"Link states: {dict(states)}")
    print(f"Speed range: {min(speeds)} - {max(speeds)} Mbps")
    print(f"Vendors: {', '.join(sorted(vendors))}")
    
    # Check MAC addresses
    mac_addresses = [i.mac_address for i in interfaces if i.mac_address]
    print(f"MAC addresses: {len(mac_addresses)} interfaces have MAC addresses")
    
    # Sample MAC address format
    if mac_addresses:
        sample_mac = mac_addresses[0]
        print(f"Sample MAC: {sample_mac} (format: {'valid' if ':' in sample_mac and len(sample_mac.split(':')) == 6 else 'invalid'})")
    print()


def demo_interface_details():
    """Show detailed interface information."""
    print("=== Interface Details ===")
    
    provider = MockDataProvider()
    
    # Get details for specific interfaces
    interface_names = ['eth0', 'wlan0', 'lo', 'nonexistent']
    
    for name in interface_names:
        interface = provider.get_interface_by_name(name)
        if interface:
            print(f"{name}:")
            print(f"   Type: {interface.interface_type.value}")
            print(f"   State: {interface.link_state.value}")
            print(f"   MAC: {interface.mac_address or 'N/A'}")
            print(f"   IPs: {', '.join(interface.ip_addresses) or 'None'}")
            print(f"   Speed: {interface.speed or 'N/A'} Mbps")
            print(f"   Vendor: {interface.vendor or 'N/A'}")
            print(f"   Flags: {', '.join(interface.flags) or 'None'}")
        else:
            print(f"{name}: Not found")
        print()


def demo_usage_examples():
    """Show practical usage examples."""
    print("=== Usage Examples ===")
    
    print("1. Enable mock mode in container:")
    print("   docker run -e NETGRID_MOCK_MODE=1 myapp")
    print()
    
    print("2. Test with specific configuration:")
    print("   NETGRID_MOCK_MODE=1 NETGRID_MOCK_INCLUDE_VIRTUAL=false netgrid")
    print()
    
    print("3. Programmatic usage:")
    print("   provider = MockDataProvider(include_filtered=True)")
    print("   interfaces = provider.get_mock_interfaces()")
    print()
    
    print("4. Environment detection:")
    print(f"   Current mock mode enabled: {MockDataProvider.is_mock_mode_enabled()}")
    print()


def main():
    """Run all demos."""
    print("NetGrid Mock Data Provider Demo")
    print("=" * 50)
    print()
    
    try:
        demo_basic_mock_interfaces()
        demo_configuration_options()
        demo_environment_variables()
        demo_custom_interfaces()
        demo_realistic_data()
        demo_interface_details()
        demo_usage_examples()
        
        print("Demo completed successfully!")
        print()
        print("To use mock mode:")
        print("  export NETGRID_MOCK_MODE=1")
        print("  # Then run your NetGrid application")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())