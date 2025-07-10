#!/bin/bash

# Extract interface names from the ips file and run ethtool on each
# Output will be appended to ethtool_info.txt in the current directory

output_file_name="ethtool_info.txt"

# Clear the output file if it exists
true > "$output_file_name"

# Extract interface names (lines that start with a number followed by colon and interface name)
# Pattern matches: number: interface_name:
grep -E '^[0-9]+: [a-zA-Z0-9]+:' ips | while read -r line; do
    # Extract just the interface name (second field after splitting on colon and space)
    interface_name=$(echo "$line" | awk -F': ' '{print $2}' | awk '{print $1}')
    
    echo "Processing interface: $interface_name" | tee -a "$output_file_name"
    echo "==========================================" | tee -a "$output_file_name"
    
    # Run ethtool and append output to file
    ethtool "$interface_name" 2>&1 | tee -a "$output_file_name"
    
    echo "" | tee -a "$output_file_name"
    echo "------------------------------------------" | tee -a "$output_file_name"
    echo "" | tee -a "$output_file_name"
done

echo "Ethtool information has been written to $output_file_name" 