#!/usr/bin/env python3

import re
import sys

def parse_ips_file(filename):
    """Parse the ips file to extract interface information."""
    interfaces = {}
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by interface blocks (lines starting with number: interface:)
    interface_blocks = re.split(r'\n(?=\d+:)', content)
    
    for block in interface_blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if not lines:
            continue
            
        # Parse first line: "2: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> ..."
        first_line = lines[0]
        match = re.match(r'(\d+):\s+([^:]+):\s+<([^>]+)>', first_line)
        if not match:
            continue
            
        interface_num = match.group(1)
        interface_name = match.group(2)
        flags = match.group(3)
        
        # Determine link state from flags
        if 'UP' in flags and 'LOWER_UP' in flags:
            link_state = 'UP'
        elif 'UP' in flags and 'NO-CARRIER' in flags:
            link_state = 'DOWN (No Carrier)'
        elif 'UP' in flags:
            link_state = 'UP'
        else:
            link_state = 'DOWN'
        
        # Extract IP address from subsequent lines
        ip_address = 'N/A'
        for line in lines[1:]:
            if line.strip().startswith('inet '):
                ip_match = re.search(r'inet\s+([0-9.]+/[0-9]+)', line)
                if ip_match:
                    ip_address = ip_match.group(1)
                break
        
        interfaces[interface_name] = {
            'link_state': link_state,
            'ip_address': ip_address
        }
    
    return interfaces

def parse_ethtool_file(filename):
    """Parse the ethtool_info.txt file to extract physical media information."""
    media_types = {}
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by interface processing blocks
    interface_blocks = re.split(r'Processing interface: (\w+)\n==========================================', content)
    
    for i in range(1, len(interface_blocks), 2):
        if i + 1 >= len(interface_blocks):
            break
            
        interface_name = interface_blocks[i]
        block_content = interface_blocks[i + 1]
        
        # Extract Port information
        port_match = re.search(r'Port:\s+([^\n]+)', block_content)
        if port_match:
            port = port_match.group(1).strip()
            # Map port types to more readable names
            if port == 'Twisted Pair':
                media_type = 'Ethernet (Copper)'
            elif port == 'FIBRE':
                media_type = 'Fiber'
            else:
                media_type = port
        else:
            media_type = 'Unknown'
        
        media_types[interface_name] = media_type
    
    return media_types

def create_ascii_table(interfaces, media_types):
    """Create an ASCII table from the interface data."""
    
    # Table headers
    headers = ['Interface', 'Link State', 'IP Address', 'Media Type']
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    
    # Find maximum width for each column
    for interface_name, data in interfaces.items():
        col_widths[0] = max(col_widths[0], len(interface_name))
        col_widths[1] = max(col_widths[1], len(data['link_state']))
        col_widths[2] = max(col_widths[2], len(data['ip_address']))
        
        media_type = media_types.get(interface_name, 'Unknown')
        col_widths[3] = max(col_widths[3], len(media_type))
    
    # Create the table
    table = []
    
    # Header row
    header_row = '| ' + ' | '.join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + ' |'
    table.append(header_row)
    
    # Separator row
    separator = '|' + '|'.join('-' * (w + 2) for w in col_widths) + '|'
    table.append(separator)
    
    # Data rows
    for interface_name in sorted(interfaces.keys()):
        data = interfaces[interface_name]
        media_type = media_types.get(interface_name, 'Unknown')
        
        row = '| ' + interface_name.ljust(col_widths[0]) + ' | ' + \
              data['link_state'].ljust(col_widths[1]) + ' | ' + \
              data['ip_address'].ljust(col_widths[2]) + ' | ' + \
              media_type.ljust(col_widths[3]) + ' |'
        table.append(row)
    
    return '\n'.join(table)

def main():
    try:
        # Parse the data files
        interfaces = parse_ips_file('ips')
        media_types = parse_ethtool_file('ethtool_info.txt')
        
        # Create and display the table
        table = create_ascii_table(interfaces, media_types)
        print("Network Interface Summary")
        print("=" * 50)
        print()
        print(table)
        
        # Write to file
        with open('interface_table.txt', 'w') as f:
            f.write("Network Interface Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(table + "\n")
        
        print(f"\nTable has been saved to interface_table.txt")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file {e.filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 