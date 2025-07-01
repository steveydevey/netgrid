import click
from netgrid.core.interface_collector import get_all_interfaces

@click.command()
@click.option('--show-ipv6', is_flag=True, help='Show IPv6 addresses in addition to IPv4')
def main(show_ipv6):
    """
    NetGrid: Display up-to-date network interface information in a table.
    """
    # Collect up-to-date interface data
    interfaces = get_all_interfaces()

    # Filter out unwanted interfaces
    filtered = [iface for iface in interfaces if not (
        iface.name.startswith('veth') or 
        iface.name.startswith('br-') or
        iface.name == 'lo' or
        iface.name.startswith('tailscale') or
        iface.name == 'vmsgohere'
    )]

    if not filtered:
        click.echo("No network interfaces found (after filtering).")
        return

    # Print a simple table (placeholder for now)
    header = f"{'Name':<15} {'State':<8} {'Speed':<10} {'MAC':<20} {'IP Addresses'}"
    click.echo(header)
    click.echo('-' * len(header))
    for iface in filtered:
        # Format speed
        if iface.speed:
            if iface.speed >= 1000:
                speed_str = f"{iface.speed//1000}Gbps"
            else:
                speed_str = f"{iface.speed}Mbps"
        else:
            speed_str = '-'
        
        # Filter IP addresses based on --show-ipv6 flag
        if show_ipv6:
            # Show all IP addresses
            ips = ', '.join(iface.ip_addresses) if iface.ip_addresses else '-'
        else:
            # Show only IPv4 addresses
            ipv4_addresses = [ip for ip in iface.ip_addresses if ':' not in ip]
            ips = ', '.join(ipv4_addresses) if ipv4_addresses else '-'
        
        click.echo(f"{iface.name:<15} {iface.link_state.value:<8} {speed_str:<10} {iface.mac_address or '-':<20} {ips}")

if __name__ == "__main__":
    main() 