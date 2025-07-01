#!/usr/bin/env python3

import subprocess
import re
import time
import requests
import json
from typing import Dict, Optional

def get_network_interfaces() -> Dict[str, Dict]:
    """Get all network interfaces and their information"""
    interfaces = {}
    
    try:
        # Get interface information using ip command
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running ip addr show: {result.stderr}")
            return interfaces
        
        current_interface = None
        for line in result.stdout.split('\n'):
            # Match interface lines
            interface_match = re.match(r'^\d+:\s+(\w+):', line)
            if interface_match:
                current_interface = interface_match.group(1)
                if current_interface != 'lo':  # Skip loopback
                    interfaces[current_interface] = {
                        'mac': None,
                        'ip': None,
                        'state': None,
                        'media_type': 'Ethernet (Copper)'
                    }
                    # Determine media type based on interface name
                    if current_interface.startswith('ens'):
                        interfaces[current_interface]['media_type'] = 'Fiber'
            
            # Get MAC address
            if current_interface and current_interface in interfaces:
                mac_match = re.search(r'link/ether\s+([0-9a-f:]+)', line)
                if mac_match:
                    interfaces[current_interface]['mac'] = mac_match.group(1)
                
                # Get IP address
                ip_match = re.search(r'inet\s+([0-9.]+/[0-9]+)', line)
                if ip_match:
                    interfaces[current_interface]['ip'] = ip_match.group(1)
        
        # Get link states
        for interface in interfaces:
            try:
                result = subprocess.run(['ip', 'link', 'show', interface], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    if 'state UP' in result.stdout:
                        if 'LOWER_UP' in result.stdout:
                            interfaces[interface]['state'] = 'UP'
                        else:
                            interfaces[interface]['state'] = 'DOWN (No Carrier)'
                    else:
                        interfaces[interface]['state'] = 'DOWN'
            except Exception as e:
                print(f"Error getting state for {interface}: {e}")
                interfaces[interface]['state'] = 'Unknown'
    
    except Exception as e:
        print(f"Error getting network interfaces: {e}")
    
    return interfaces

def get_vendor_from_api(mac: str) -> Optional[str]:
    """Get vendor information from macvendors.com API"""
    try:
        # Add delay to avoid rate limiting
        time.sleep(1)
        
        response = requests.get(f'https://api.macvendors.com/{mac}', timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        elif response.status_code == 429:
            return "Rate Limited"
        else:
            return None
    except Exception as e:
        print(f"API error for {mac}: {e}")
        return None

def get_vendor_local(mac: str) -> Optional[str]:
    """Get vendor from local OUI database"""
    if not mac:
        return None
    
    # Extract OUI (first 3 octets)
    oui = ':'.join(mac.split(':')[:3]).upper()
    
    # Local OUI database (common vendors)
    oui_database = {
        'C4:34:6B': 'Hewlett Packard',
        'A0:36:9F': 'Intel Corporation',
        '40:A8:F0': 'Hewlett Packard',
        '26:5E:E1': 'Docker Inc',
        '2A:58:2D': 'Virtual Interface',
        '00:15:5D': 'Microsoft Corporation',
        '00:0C:29': 'VMware Inc',
        '00:50:56': 'VMware Inc',
        '52:54:00': 'QEMU Virtual NIC',
    }
    
    return oui_database.get(oui)

def main():
    print("Network Interface Vendor Lookup (Python)")
    print("========================================")
    
    # Get network interfaces
    interfaces = get_network_interfaces()
    
    if not interfaces:
        print("No network interfaces found")
        return
    
    # Create output table
    output_lines = [
        "Network Interface Summary with Vendor Information",
        "==================================================",
        "",
        "| Interface | Link State        | IP Address         | Media Type        | Vendor            |",
        "|-----------|-------------------|--------------------|-------------------|-------------------|"
    ]
    
    # Process each interface
    for interface, info in interfaces.items():
        print(f"Processing interface: {interface}")
        
        if info['mac']:
            print(f"  MAC Address: {info['mac']}")
            
            # Try local lookup first
            vendor = get_vendor_local(info['mac'])
            if not vendor:
                print("  Trying API lookup...")
                vendor = get_vendor_from_api(info['mac'])
            
            if not vendor:
                vendor = "Unknown"
            
            print(f"  Vendor: {vendor}")
        else:
            vendor = "No MAC"
            print("  No MAC address found")
        
        # Format the table row
        ip_addr = info['ip'] if info['ip'] else 'N/A'
        state = info['state'] if info['state'] else 'Unknown'
        media_type = info['media_type']
        
        row = f"| {interface:<9} | {state:<16} | {ip_addr:<18} | {media_type:<18} | {vendor:<18} |"
        output_lines.append(row)
        
        print("  Added to table")
        print()
    
    # Write to file
    output_file = "interface_table_with_vendors_python.txt"
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Vendor lookup complete! Results saved to: {output_file}")
    print()
    print("Updated table:")
    print("==============")
    print('\n'.join(output_lines))

if __name__ == "__main__":
    main() 