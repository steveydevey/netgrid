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

from ..core.data_models import NetworkInterface


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
        if not interface.ip_addresses:
            return "[dim]-[/dim]"
        
        formatted_addresses = []
        for ip in interface.ip_addresses:
            if not show_ipv6 and ':' in ip:  # Skip IPv6 if not requested
                continue
            formatted_addresses.append(ip)
        
        if not formatted_addresses:
            return "[dim]-[/dim]"
        
        return ", ".join(formatted_addresses)
    
    def print_table(self, interfaces: List[NetworkInterface], 
                   show_vendors: bool = True,
                   show_ipv6: bool = False,
                   show_summary: bool = False,
                   sort_by: str = "name") -> None:
        """
        Print the interfaces table to the console.
        
        Args:
            interfaces: List of network interface objects
            show_vendors: Whether to include vendor information
            show_ipv6: Whether to show IPv6 addresses
            show_summary: Whether to show interface summary
            sort_by: Column to sort by
        """
        # Format and print the table
        table_output = self.format_interfaces_table(
            interfaces, show_vendors, show_ipv6, sort_by
        )
        self.console.print(table_output)
    
    def format_error(self, error_message: str) -> str:
        """
        Format an error message.
        
        Args:
            error_message: Error message to format
            
        Returns:
            Formatted error message
        """
        return f"[red]Error: {error_message}[/red]"
    
    def format_warning(self, warning_message: str) -> str:
        """
        Format a warning message.
        
        Args:
            warning_message: Warning message to format
            
        Returns:
            Formatted warning message
        """
        return f"[yellow]Warning: {warning_message}[/yellow]"
    
    def format_info(self, info_message: str) -> str:
        """
        Format an info message.
        
        Args:
            info_message: Info message to format
            
        Returns:
            Formatted info message
        """
        return f"[blue]Info: {info_message}[/blue]" 