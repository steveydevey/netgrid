#!/bin/bash

# Script to get vendor information for network interfaces
# Uses macvendors.com API to lookup OUI information

echo "Network Interface Vendor Lookup"
echo "================================"

# Create output file
output_file="interface_table_with_vendors.txt"

# Clear the output file
> "$output_file"

# Add header to output file
cat << 'EOF' > "$output_file"
Network Interface Summary with Vendor Information
==================================================

| Interface | Link State        | IP Address         | Media Type        | Vendor            |
|-----------|-------------------|--------------------|-------------------|-------------------|
EOF

# Function to get vendor from MAC address
get_vendor() {
    local mac="$1"
    local vendor
    
    # Query macvendors.com API
    vendor=$(curl -s "https://api.macvendors.com/$mac" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$vendor" ]; then
        echo "$vendor"
    else
        echo "Unknown"
    fi
}

# Get interface information and process each one
ip addr show | grep -E "^[0-9]+: [a-zA-Z0-9]+:" | while read -r line; do
    # Extract interface name
    interface=$(echo "$line" | awk -F': ' '{print $2}' | awk '{print $1}')
    
    # Skip loopback interface
    if [ "$interface" = "lo" ]; then
        continue
    fi
    
    echo "Processing interface: $interface"
    
    # Get MAC address for this interface
    mac=$(ip link show "$interface" | grep -o -E "link/ether [0-9a-f:]+" | awk '{print $2}')
    
    if [ -n "$mac" ]; then
        echo "  MAC Address: $mac"
        
        # Get vendor information
        vendor=$(get_vendor "$mac")
        echo "  Vendor: $vendor"
        
        # Get link state
        link_state=$(ip link show "$interface" | grep -o "state [A-Z]\+" | awk '{print $2}')
        
        # Get IP address
        ip_addr=$(ip addr show "$interface" | grep -E "inet [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" | awk '{print $2}' | head -1)
        if [ -z "$ip_addr" ]; then
            ip_addr="N/A"
        fi
        
        # Determine media type based on interface name
        if [[ "$interface" =~ ^ens ]]; then
            media_type="Fiber"
        else
            media_type="Ethernet (Copper)"
        fi
        
        # Format link state for display
        if [ "$link_state" = "UP" ]; then
            # Check if interface has carrier
            if ip link show "$interface" | grep -q "LOWER_UP"; then
                display_state="UP"
            else
                display_state="DOWN (No Carrier)"
            fi
        else
            display_state="DOWN"
        fi
        
        # Add to output file
        printf "| %-9s | %-16s | %-18s | %-18s | %-18s |\n" \
               "$interface" "$display_state" "$ip_addr" "$media_type" "$vendor" >> "$output_file"
        
        echo "  Added to table"
    else
        echo "  No MAC address found"
    fi
    
    echo ""
done

echo "Vendor lookup complete! Results saved to: $output_file"
echo ""
echo "Updated table:"
echo "=============="
cat "$output_file" 