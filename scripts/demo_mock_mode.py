#!/usr/bin/env python3
"""
Demo script for NetGrid mock mode functionality.

This script demonstrates how to use NetGrid with mock data for testing
in isolated environments like containers.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import netgrid
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from netgrid.core.interface_collector import InterfaceCollector
from netgrid.core.mock_data_provider import MockDataProvider
from netgrid.core.data_models import InterfaceType, LinkState
from netgrid.display.table_formatter import TableFormatter


def demo_basic_mock_mode():
    """Demonstrate basic mock mode functionality."""
    print("=== Basic Mock Mode Demo ===")
    print("Using mock data with default settings")
    print()
    
    # Create collector with mock data enabled
    collector = InterfaceCollector(use_mock_data=True)
    interfaces = collector.get_all_interfaces()
    
    print(f"Found {len(interfaces)} mock interfaces:")
    for interface in interfaces:
        status = "UP" if interface.is_up else "DOWN"
        ip_info = f" ({interface.primary_ip})" if interface.primary_ip else ""
        vendor_info = f" - {interface.vendor}" if interface.vendor else ""
        print(f"  {interface.name}: {status}{ip_info}{vendor_info}")
    print()


def demo_custom_mock_config():
    """Demonstrate custom mock configuration."""
    print("=== Custom Mock Configuration Demo ===")
    
    # Demo 1: Include filtered interfaces
    print("1. Including normally filtered interfaces (veth, br-, tailscale):")
    provider = MockDataProvider(include_filtered=True)
    interfaces = provider.get_mock_interfaces()
    
    filtered_interfaces = [iface for iface in interfaces 
                          if any(iface.name.startswith(prefix) 
                                for prefix in ['veth', 'br-', 'tailscale'])]
    
    for interface in filtered_interfaces:
        print(f"  {interface.name}: {interface.interface_type.value}")
    print()
    
    # Demo 2: Exclude virtual interfaces
    print("2. Excluding virtual interfaces (bonds, bridges, etc.):")
    provider = MockDataProvider(include_virtual=False)
    interfaces = provider.get_mock_interfaces()
    
    print(f"Physical interfaces only ({len(interfaces)} total):")
    for interface in interfaces:
        if interface.interface_type.value in ['physical', 'wireless', 'loopback']:
            print(f"  {interface.name}: {interface.interface_type.value}")
    print()


def demo_environment_variables():
    """Demonstrate using environment variables to control mock mode."""
    print("=== Environment Variable Demo ===")
    
    # Set environment variables
    os.environ['NETGRID_MOCK_MODE'] = '1'
    os.environ['NETGRID_MOCK_INCLUDE_VIRTUAL'] = 'false'
    os.environ['NETGRID_MOCK_INCLUDE_FILTERED'] = 'true'
    
    print("Environment variables set:")
    print("  NETGRID_MOCK_MODE=1")
    print("  NETGRID_MOCK_INCLUDE_VIRTUAL=false")
    print("  NETGRID_MOCK_INCLUDE_FILTERED=true")
    print()
    
    # Create collector - it will automatically detect mock mode
    collector = InterfaceCollector()
    interfaces = collector.get_all_interfaces()
    
    print("Resulting interfaces:")
    for interface in interfaces:
        print(f"  {interface.name}: {interface.interface_type.value} - {interface.link_state.value}")
    
    # Clean up environment
    del os.environ['NETGRID_MOCK_MODE']
    del os.environ['NETGRID_MOCK_INCLUDE_VIRTUAL']
    del os.environ['NETGRID_MOCK_INCLUDE_FILTERED']
    print()


def demo_custom_interface_creation():
    """Demonstrate creating custom mock interfaces."""
    print("=== Custom Interface Creation Demo ===")
    
    # Create some custom interfaces
    custom_interfaces = [
        MockDataProvider.create_custom_interface(
            name="test-eth0",
            ip_addresses=["10.0.0.100", "fe80::1"],
            speed=10000,
            vendor="Custom Vendor Inc."
        ),
        MockDataProvider.create_custom_interface(
            name="test-wifi0",
            interface_type=InterfaceType.WIRELESS,
            ip_addresses=["192.168.1.200"],
            speed=150,
            vendor="Wireless Corp"
        ),
        MockDataProvider.create_custom_interface(
            name="test-down0",
            link_state=LinkState.DOWN,
            speed=None
        )
    ]
    
    print("Custom interfaces created:")
    for interface in custom_interfaces:
        status = "UP" if interface.is_up else "DOWN"
        speed_info = f" ({interface.speed} Mbps)" if interface.speed else ""
        print(f"  {interface.name}: {status}{speed_info}")
        if interface.ip_addresses:
            print(f"    IPs: {', '.join(interface.ip_addresses)}")
        if interface.vendor:
            print(f"    Vendor: {interface.vendor}")
    print()


def demo_table_output():
    """Demonstrate table output with mock data."""
    print("=== Table Output Demo ===")
    print("Displaying mock interfaces in table format:")
    print()
    
    # Create collector with mock data
    collector = InterfaceCollector(use_mock_data=True)
    interfaces = collector.get_all_interfaces()
    
    # Filter out interfaces as the CLI does
    filtered = [iface for iface in interfaces if not (
        iface.name.startswith('veth') or 
        iface.name.startswith('br-') or
        iface.name == 'lo' or
        iface.name.startswith('tailscale') or
        iface.name == 'vmsgohere'
    )]
    
    try:
        # Try to use the table formatter
        formatter = TableFormatter()
        formatter.print_table(
            interfaces=filtered,
            show_vendors=True,
            show_ipv6=True,
            show_summary=True
        )
    except Exception as e:
        # Fallback to simple text output if table formatter isn't available
        print("Table formatter not available, using simple output:")
        print(f"{'Interface':<12} {'State':<6} {'Speed':<8} {'IP Address':<15} {'Vendor'}")
        print("-" * 70)
        
        for interface in filtered:
            status = "UP" if interface.is_up else "DOWN"
            speed = f"{interface.speed}" if interface.speed else "N/A"
            ip = interface.primary_ip or "N/A"
            vendor = interface.vendor or "N/A"
            print(f"{interface.name:<12} {status:<6} {speed:<8} {ip:<15} {vendor}")


def demo_container_usage():
    """Show how to use mock mode in containers."""
    print("=== Container Usage Demo ===")
    print("To use NetGrid with mock data in a container:")
    print()
    print("1. Set environment variable before running:")
    print("   export NETGRID_MOCK_MODE=1")
    print("   netgrid")
    print()
    print("2. Or set inline:")
    print("   NETGRID_MOCK_MODE=1 netgrid")
    print()
    print("3. With custom configuration:")
    print("   NETGRID_MOCK_MODE=1 \\")
    print("   NETGRID_MOCK_INCLUDE_VIRTUAL=true \\")
    print("   NETGRID_MOCK_INCLUDE_FILTERED=true \\")
    print("   netgrid")
    print()
    print("4. In a Dockerfile:")
    print("   ENV NETGRID_MOCK_MODE=1")
    print("   RUN netgrid")
    print()


def main():
    """Run all demos."""
    print("NetGrid Mock Mode Demonstration")
    print("=" * 50)
    print()
    
    try:
        demo_basic_mock_mode()
        demo_custom_mock_config()
        demo_environment_variables()
        demo_custom_interface_creation()
        demo_table_output()
        demo_container_usage()
        
        print("Demo completed successfully!")
        print()
        print("To test mock mode with the actual NetGrid CLI:")
        print("  NETGRID_MOCK_MODE=1 python -m netgrid.cli.main")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())