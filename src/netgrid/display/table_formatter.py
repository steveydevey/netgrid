"""
Table formatting module for NetGrid.

This module provides functionality to format network interface information
into beautiful, readable tables with colors and styling.
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
import logging

from ..core.data_models import NetworkInterface

logger = logging.getLogger(__name__)


class TableFormatter:
    """
    Formats network interface data into beautiful tables.
    
    Uses Rich library for enhanced terminal output with colors,
    styling, and proper alignment.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the table formatter.
        
        Args:
            console: Rich console instance (creates new one if None)
        """
        self.console = console or Console()
    
    def format_interfaces_table(self, interfaces: List[NetworkInterface], 
                               show_vendors: bool = True,
                               show_ipv6: bool = False,
                               sort_by: str = "name") -> str:
        """
        Format network interfaces into a table.
        
        Args:
            interfaces: List of network interface objects
            show_vendors: Whether to include vendor information
            show_ipv6: Whether to show IPv6 addresses
            sort_by: Column to sort by (name, state, speed, mac, vendor, ip)
            
        Returns:
            Formatted table string
        """
        # Sort interfaces before formatting
        sorted_interfaces = self.sort_interfaces(interfaces, sort_by)
        
        table = Table(
            title="Network Interfaces",
            title_style="bold blue",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            show_edge=True,
            show_lines=True
        )
        
        # Define columns
        columns = [
            ("Name", "cyan", "left"),
            ("Speed", "yellow", "center"),
            ("MAC", "blue", "left"),
            ("MTU", "white", "center"),
            ("IP Config", "white", "center"),
        ]
        
        if show_vendors:
            columns.append(("Vendor", "magenta", "left"))
        
        columns.append(("IP Addresses", "white", "left"))
        
        # Add columns to table
        for column_name, style, justify in columns:
            table.add_column(column_name, style=style, justify=justify)
        
        # Add rows
        for interface in sorted_interfaces:
            row_data = self._format_interface_row(
                interface, show_vendors, show_ipv6
            )
            table.add_row(*row_data)
        
        # Create panel for better presentation
        panel = Panel(
            Align.center(table),
            title="[bold blue]NetGrid[/bold blue]",
            subtitle="[italic]Network Interface Information[/italic]",
            border_style="blue"
        )
        
        return panel
    
    def sort_interfaces(self, interfaces: List[NetworkInterface], sort_by: str) -> List[NetworkInterface]:
        """
        Sort interfaces by the specified column.
        
        Args:
            interfaces: List of network interface objects
            sort_by: Column to sort by (name, state, speed, mac, vendor, ip)
            
        Returns:
            Sorted list of interfaces
        """
        if not interfaces:
            return interfaces
        
        # Define sort key functions
        sort_keys = {
            "name": lambda x: x.name.lower(),  # Default sort by name
            "state": lambda x: (0 if x.is_up else 1, x.name.lower()),  # UP first, then by name
            "speed": lambda x: (x.speed or 0, x.name.lower()),  # None speeds last
            "mac": lambda x: x.mac_address or "",
            "vendor": lambda x: (x.vendor or "", x.name.lower()),
            "ip": lambda x: (x.primary_ip or "", x.name.lower()),
        }
        
        # Get the sort key function, default to name
        sort_key = sort_keys.get(sort_by.lower(), sort_keys["name"])
        
        # Sort the interfaces
        return sorted(interfaces, key=sort_key)
    
    def _format_interface_row(self, interface: NetworkInterface, 
                             show_vendors: bool, show_ipv6: bool) -> List[str]:
        """
        Format a single interface row.
        
        Args:
            interface: Network interface object
            show_vendors: Whether to include vendor information
            show_ipv6: Whether to show IPv6 addresses
            
        Returns:
            List of formatted cell values
        """
        # Interface name with color based on state
        if interface.is_up:
            name = f"[green]● {interface.name}[/green]"
        else:
            name = f"[red]● {interface.name}[/red]"
        
        # Speed
        if interface.speed:
            speed = f"[yellow]{interface.speed}[/yellow]"
        else:
            speed = "[dim]-[/dim]"
        
        # MAC address
        mac = f"[blue]{interface.mac_address}[/blue]"
        
        # MTU
        if interface.mtu:
            mtu = f"[white]{interface.mtu}[/white]"
        else:
            mtu = "[dim]-[/dim]"
        
        # IP Config type
        ip_config = f"[white]{interface.ip_config_type}[/white]" if interface.ip_config_type else "[dim]-[/dim]"
        
        # Vendor (if enabled)
        vendor = ""
        if show_vendors and hasattr(interface, 'vendor') and interface.vendor:
            vendor = f"[magenta]{interface.vendor}[/magenta]"
        elif show_vendors:
            vendor = "[dim]-[/dim]"
        
        # IP addresses
        ip_addresses = self._format_ip_addresses(interface, show_ipv6)
        
        # Build row data
        row_data = [name, speed, mac, mtu, ip_config]
        
        if show_vendors:
            row_data.append(vendor)
        
        row_data.append(ip_addresses)
        
        return row_data
    
    def _format_ip_addresses(self, interface: NetworkInterface, 
                            show_ipv6: bool) -> str:
        """
        Format IP addresses for display.
        
        Args:
            interface: Network interface object
            show_ipv6: Whether to show IPv6 addresses
            
        Returns:
            Formatted IP addresses string
        """
        addresses = []
        
        # Separate IPv4 and IPv6 addresses
        ipv4_addresses = [ip for ip in interface.ip_addresses if ':' not in ip]
        ipv6_addresses = [ip for ip in interface.ip_addresses if ':' in ip]
        
        # Add IPv4 addresses
        if ipv4_addresses:
            for ip in ipv4_addresses:
                addresses.append(f"[green]{ip}[/green]")
        
        # Add IPv6 addresses if requested
        if show_ipv6 and ipv6_addresses:
            for ip in ipv6_addresses:
                addresses.append(f"[cyan]{ip}[/cyan]")
        
        if addresses:
            return ", ".join(addresses)
        else:
            return "[dim]-[/dim]"
    
    def format_summary(self, interfaces: List[NetworkInterface]) -> str:
        """
        Format a summary of network interfaces.
        
        Args:
            interfaces: List of network interface objects
            
        Returns:
            Formatted summary string
        """
        total_interfaces = len(interfaces)
        up_interfaces = sum(1 for i in interfaces if i.is_up)
        down_interfaces = total_interfaces - up_interfaces
        
        # Count by type
        ethernet_count = sum(1 for i in interfaces if 'eno' in i.name or 'ens' in i.name)
        wireless_count = sum(1 for i in interfaces if 'wlan' in i.name or 'wifi' in i.name)
        other_count = total_interfaces - ethernet_count - wireless_count
        
        summary_table = Table(
            title="Interface Summary",
            title_style="bold green",
            show_header=True,
            header_style="bold",
            border_style="green"
        )
        
        summary_table.add_column("Metric", style="cyan", justify="left")
        summary_table.add_column("Count", style="yellow", justify="right")
        
        summary_table.add_row("Total Interfaces", str(total_interfaces))
        summary_table.add_row("Up", f"[green]{up_interfaces}[/green]")
        summary_table.add_row("Down", f"[red]{down_interfaces}[/red]")
        summary_table.add_row("Ethernet", str(ethernet_count))
        summary_table.add_row("Wireless", str(wireless_count))
        summary_table.add_row("Other", str(other_count))
        
        return summary_table
    
    def format_interface_details(self, interface: NetworkInterface) -> str:
        """
        Format detailed information for a single interface.
        
        Args:
            interface: Network interface object
            
        Returns:
            Formatted details string
        """
        details_table = Table(
            title=f"Interface Details: {interface.name}",
            title_style="bold blue",
            show_header=False,
            border_style="blue",
            show_edge=True
        )
        
        details_table.add_column("Property", style="cyan", justify="left")
        details_table.add_column("Value", style="white", justify="left")
        
        # Basic information
        details_table.add_row("Name", interface.name)
        details_table.add_row("State", 
                             "[green]UP[/green]" if interface.is_up else "[red]DOWN[/red]")
        details_table.add_row("MAC Address", interface.mac_address)
        
        if interface.speed:
            details_table.add_row("Speed", interface.speed)
        
        if interface.mtu:
            details_table.add_row("MTU", str(interface.mtu))
        
        if hasattr(interface, 'driver') and interface.driver:
            details_table.add_row("Driver", interface.driver)
        
        if hasattr(interface, 'vendor') and interface.vendor:
            details_table.add_row("Vendor", interface.vendor)
        
        # IP addresses
        ipv4_addresses = [ip for ip in interface.ip_addresses if ':' not in ip]
        ipv6_addresses = [ip for ip in interface.ip_addresses if ':' in ip]
        
        if ipv4_addresses:
            details_table.add_row("IPv4 Addresses", 
                                 ", ".join(ipv4_addresses))
        
        if ipv6_addresses:
            details_table.add_row("IPv6 Addresses", 
                                 ", ".join(ipv6_addresses))
        
        return details_table
    
    def print_table(self, interfaces: List[NetworkInterface], 
                   show_vendors: bool = True,
                   show_ipv6: bool = False,
                   show_summary: bool = False,
                   sort_by: str = "mac") -> None:
        """
        Print formatted table to console.
        
        Args:
            interfaces: List of network interface objects
            show_vendors: Whether to include vendor information
            show_ipv6: Whether to show IPv6 addresses
            show_summary: Whether to show summary information
            sort_by: Column to sort by (name, state, speed, mac, vendor, ip)
        """
        # Print main table
        table = self.format_interfaces_table(interfaces, show_vendors, show_ipv6, sort_by)
        self.console.print(table)
        
        # Print summary if requested
        if show_summary:
            self.console.print()  # Add spacing
            summary = self.format_summary(interfaces)
            self.console.print(summary)
    
    def print_interface_details(self, interface: NetworkInterface) -> None:
        """
        Print detailed information for a single interface.
        
        Args:
            interface: Network interface object
        """
        details = self.format_interface_details(interface)
        self.console.print(details)
    
    def format_error(self, error_message: str) -> str:
        """
        Format error messages.
        
        Args:
            error_message: Error message to format
            
        Returns:
            Formatted error string
        """
        return f"[red]Error:[/red] {error_message}"
    
    def format_warning(self, warning_message: str) -> str:
        """
        Format warning messages.
        
        Args:
            warning_message: Warning message to format
            
        Returns:
            Formatted warning string
        """
        return f"[yellow]Warning:[/yellow] {warning_message}"
    
    def format_info(self, info_message: str) -> str:
        """
        Format info messages.
        
        Args:
            info_message: Info message to format
            
        Returns:
            Formatted info string
        """
        return f"[blue]Info:[/blue] {info_message}" 