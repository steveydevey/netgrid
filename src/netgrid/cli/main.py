import click
from netgrid.core.interface_collector import InterfaceCollector
from netgrid.display.table_formatter import TableFormatter
from netgrid.display.color_manager import ColorManager, ColorScheme

@click.command()
@click.option('--show-ipv6', is_flag=True, help='Show IPv6 addresses in addition to IPv4')
@click.option('--no-vendors', is_flag=True, help='Disable vendor lookup')
@click.option('--show-summary', is_flag=True, help='Show interface summary')
@click.option('--color-scheme', type=click.Choice(['default', 'dark', 'light', 'high_contrast', 'colorblind']), 
              default='default', help='Color scheme to use')
def main(show_ipv6, no_vendors, show_summary, color_scheme):
    """
    NetGrid: Display up-to-date network interface information in a table.
    """
    # Initialize color manager
    try:
        scheme = ColorScheme(color_scheme)
        color_manager = ColorManager(scheme)
    except ValueError:
        click.echo(f"Error: Invalid color scheme '{color_scheme}'")
        return
    
    # Initialize interface collector with vendor lookup toggle
    try:
        collector = InterfaceCollector(enable_vendor_lookup=not no_vendors)
    except Exception as e:
        click.echo(f"Error initializing interface collector: {e}")
        return
    
    # Initialize table formatter
    formatter = TableFormatter()
    
    try:
        # Collect up-to-date interface data
        interfaces = collector.get_all_interfaces()
        
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
        
        # Display the table using the formatter
        formatter.print_table(
            interfaces=filtered,
            show_vendors=not no_vendors,
            show_ipv6=show_ipv6,
            show_summary=show_summary
        )
        
    except Exception as e:
        click.echo(f"Error displaying interfaces: {e}")
        return

if __name__ == "__main__":
    main() 