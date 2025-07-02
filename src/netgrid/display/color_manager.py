"""
Color management module for NetGrid.

This module provides color schemes and themes for consistent
styling across the NetGrid application.
"""

from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ColorScheme(Enum):
    """Available color schemes for NetGrid."""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    HIGH_CONTRAST = "high_contrast"
    COLORBLIND = "colorblind"


class ColorManager:
    """
    Manages color schemes and themes for NetGrid.
    
    Provides consistent color definitions and theme management
    for the application's display components.
    """
    
    def __init__(self, scheme: ColorScheme = ColorScheme.DEFAULT):
        """
        Initialize the color manager.
        
        Args:
            scheme: Color scheme to use
        """
        self.scheme = scheme
        self.colors = self._get_color_scheme(scheme)
    
    def _get_color_scheme(self, scheme: ColorScheme) -> Dict[str, str]:
        """
        Get color definitions for a specific scheme.
        
        Args:
            scheme: Color scheme enum
            
        Returns:
            Dictionary of color definitions
        """
        schemes = {
            ColorScheme.DEFAULT: {
                # Interface states
                'up': 'green',
                'down': 'red',
                'unknown': 'yellow',
                
                # Interface types
                'ethernet': 'blue',
                'wireless': 'magenta',
                'virtual': 'cyan',
                'loopback': 'white',
                
                # Data types
                'ipv4': 'green',
                'ipv6': 'cyan',
                'mac': 'blue',
                'vendor': 'magenta',
                'speed': 'yellow',
                
                # UI elements
                'title': 'bold blue',
                'header': 'bold magenta',
                'border': 'blue',
                'error': 'red',
                'warning': 'yellow',
                'info': 'blue',
                'success': 'green',
                
                # Text emphasis
                'bold': 'bold',
                'dim': 'dim',
                'italic': 'italic',
            },
            
            ColorScheme.DARK: {
                # Interface states
                'up': 'bright_green',
                'down': 'bright_red',
                'unknown': 'bright_yellow',
                
                # Interface types
                'ethernet': 'bright_blue',
                'wireless': 'bright_magenta',
                'virtual': 'bright_cyan',
                'loopback': 'bright_white',
                
                # Data types
                'ipv4': 'bright_green',
                'ipv6': 'bright_cyan',
                'mac': 'bright_blue',
                'vendor': 'bright_magenta',
                'speed': 'bright_yellow',
                
                # UI elements
                'title': 'bold bright_blue',
                'header': 'bold bright_magenta',
                'border': 'bright_blue',
                'error': 'bright_red',
                'warning': 'bright_yellow',
                'info': 'bright_blue',
                'success': 'bright_green',
                
                # Text emphasis
                'bold': 'bold',
                'dim': 'dim',
                'italic': 'italic',
            },
            
            ColorScheme.LIGHT: {
                # Interface states
                'up': 'dark_green',
                'down': 'dark_red',
                'unknown': 'dark_yellow',
                
                # Interface types
                'ethernet': 'dark_blue',
                'wireless': 'dark_magenta',
                'virtual': 'dark_cyan',
                'loopback': 'black',
                
                # Data types
                'ipv4': 'dark_green',
                'ipv6': 'dark_cyan',
                'mac': 'dark_blue',
                'vendor': 'dark_magenta',
                'speed': 'dark_yellow',
                
                # UI elements
                'title': 'bold dark_blue',
                'header': 'bold dark_magenta',
                'border': 'dark_blue',
                'error': 'dark_red',
                'warning': 'dark_yellow',
                'info': 'dark_blue',
                'success': 'dark_green',
                
                # Text emphasis
                'bold': 'bold',
                'dim': 'dim',
                'italic': 'italic',
            },
            
            ColorScheme.HIGH_CONTRAST: {
                # Interface states
                'up': 'bright_green',
                'down': 'bright_red',
                'unknown': 'bright_yellow',
                
                # Interface types
                'ethernet': 'bright_white',
                'wireless': 'bright_white',
                'virtual': 'bright_white',
                'loopback': 'bright_white',
                
                # Data types
                'ipv4': 'bright_green',
                'ipv6': 'bright_cyan',
                'mac': 'bright_white',
                'vendor': 'bright_white',
                'speed': 'bright_yellow',
                
                # UI elements
                'title': 'bold bright_white',
                'header': 'bold bright_white',
                'border': 'bright_white',
                'error': 'bright_red',
                'warning': 'bright_yellow',
                'info': 'bright_cyan',
                'success': 'bright_green',
                
                # Text emphasis
                'bold': 'bold',
                'dim': 'dim',
                'italic': 'italic',
            },
            
            ColorScheme.COLORBLIND: {
                # Interface states (using shapes and patterns instead of colors)
                'up': 'green',
                'down': 'red',
                'unknown': 'yellow',
                
                # Interface types
                'ethernet': 'blue',
                'wireless': 'magenta',
                'virtual': 'cyan',
                'loopback': 'white',
                
                # Data types
                'ipv4': 'green',
                'ipv6': 'cyan',
                'mac': 'blue',
                'vendor': 'magenta',
                'speed': 'yellow',
                
                # UI elements
                'title': 'bold blue',
                'header': 'bold magenta',
                'border': 'blue',
                'error': 'red',
                'warning': 'yellow',
                'info': 'blue',
                'success': 'green',
                
                # Text emphasis
                'bold': 'bold',
                'dim': 'dim',
                'italic': 'italic',
            }
        }
        
        return schemes.get(scheme, schemes[ColorScheme.DEFAULT])
    
    def get_color(self, color_name: str) -> str:
        """
        Get a color definition by name.
        
        Args:
            color_name: Name of the color to retrieve
            
        Returns:
            Color definition string
        """
        return self.colors.get(color_name, 'white')
    
    def format_text(self, text: str, color_name: str) -> str:
        """
        Format text with a specific color.
        
        Args:
            text: Text to format
            color_name: Name of the color to apply
            
        Returns:
            Formatted text string
        """
        color = self.get_color(color_name)
        return f"[{color}]{text}[/{color}]"
    
    def format_interface_state(self, is_up: bool) -> str:
        """
        Format interface state with appropriate color.
        
        Args:
            is_up: Whether the interface is up
            
        Returns:
            Formatted state string
        """
        if is_up:
            return self.format_text("● UP", "up")
        else:
            return self.format_text("● DOWN", "down")
    
    def format_interface_type(self, interface_name: str) -> str:
        """
        Format interface type with appropriate color.
        
        Args:
            interface_name: Name of the interface
            
        Returns:
            Formatted type string
        """
        if 'eno' in interface_name or 'ens' in interface_name:
            return self.format_text(interface_name, "ethernet")
        elif 'wlan' in interface_name or 'wifi' in interface_name:
            return self.format_text(interface_name, "wireless")
        elif 'veth' in interface_name or 'br-' in interface_name:
            return self.format_text(interface_name, "virtual")
        elif 'lo' in interface_name:
            return self.format_text(interface_name, "loopback")
        else:
            return self.format_text(interface_name, "bold")
    
    def format_ip_address(self, ip: str, is_ipv6: bool = False) -> str:
        """
        Format IP address with appropriate color.
        
        Args:
            ip: IP address string
            is_ipv6: Whether this is an IPv6 address
            
        Returns:
            Formatted IP address string
        """
        color_name = "ipv6" if is_ipv6 else "ipv4"
        return self.format_text(ip, color_name)
    
    def format_mac_address(self, mac: str) -> str:
        """
        Format MAC address with appropriate color.
        
        Args:
            mac: MAC address string
            
        Returns:
            Formatted MAC address string
        """
        return self.format_text(mac, "mac")
    
    def format_vendor(self, vendor: str) -> str:
        """
        Format vendor name with appropriate color.
        
        Args:
            vendor: Vendor name string
            
        Returns:
            Formatted vendor string
        """
        return self.format_text(vendor, "vendor")
    
    def format_speed(self, speed: str) -> str:
        """
        Format speed with appropriate color.
        
        Args:
            speed: Speed string
            
        Returns:
            Formatted speed string
        """
        return self.format_text(speed, "speed")
    
    def get_table_style(self) -> Dict[str, str]:
        """
        Get table styling for the current color scheme.
        
        Returns:
            Dictionary of table style properties
        """
        return {
            'title_style': self.get_color('title'),
            'header_style': self.get_color('header'),
            'border_style': self.get_color('border'),
        }
    
    def get_message_style(self, message_type: str) -> str:
        """
        Get message styling for different types.
        
        Args:
            message_type: Type of message (error, warning, info, success)
            
        Returns:
            Color definition for the message type
        """
        return self.get_color(message_type)
    
    def change_scheme(self, scheme: ColorScheme) -> None:
        """
        Change the current color scheme.
        
        Args:
            scheme: New color scheme to use
        """
        self.scheme = scheme
        self.colors = self._get_color_scheme(scheme)
        logger.info(f"Color scheme changed to: {scheme.value}")
    
    def get_available_schemes(self) -> list:
        """
        Get list of available color schemes.
        
        Returns:
            List of color scheme names
        """
        return [scheme.value for scheme in ColorScheme]
    
    def is_colorblind_friendly(self) -> bool:
        """
        Check if current scheme is colorblind-friendly.
        
        Returns:
            True if current scheme is colorblind-friendly
        """
        return self.scheme == ColorScheme.COLORBLIND
    
    def get_scheme_info(self) -> Dict[str, Any]:
        """
        Get information about the current color scheme.
        
        Returns:
            Dictionary with scheme information
        """
        return {
            'name': self.scheme.value,
            'colorblind_friendly': self.is_colorblind_friendly(),
            'available_colors': list(self.colors.keys()),
            'total_colors': len(self.colors)
        } 