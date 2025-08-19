import click
from netgrid.core.interface_collector import InterfaceCollector
from netgrid.display.table_formatter import TableFormatter
from netgrid.display.color_manager import ColorManager, ColorScheme
from netgrid.core.constants import (
    VIRTUAL_INTERFACE_PREFIXES,
    VIRTUAL_INTERFACE_NAMES,
    VIRTUAL_INTERFACE_TAILSCALE_PREFIX,
    DEFAULT_SORT_BY,
    DEFAULT_COLOR_SCHEME,
    ERROR_INVALID_COLOR_SCHEME,
    ERROR_INIT_COLLECTOR,
    ERROR_DISPLAY_INTERFACES,
    ERROR_NO_INTERFACES,
)


def _is_virtual_interface(interface_name: str) -> bool:
    """
    Check if an interface is virtual.
    
    Args:
        interface_name: Name of the interface to check
        
    Returns:
        True if the interface is virtual, False otherwise
    """
    return (
        interface_name.startswith(VIRTUAL_INTERFACE_PREFIXES) or
        interface_name in VIRTUAL_INTERFACE_NAMES or
        interface_name.startswith(VIRTUAL_INTERFACE_TAILSCALE_PREFIX)
    )


@click.command()
@click.option('--show-ipv6', is_flag=True, help='Show IPv6 addresses in addition to IPv4')
@click.option('--no-vendors', is_flag=True, help='Disable vendor lookup')
@click.option('--include-virtual', is_flag=True, help='Include virtual interfaces (veth, br-, lo, tailscale, vmsgohere)')
@click.option('--show-summary', is_flag=True, help='Show interface summary')
@click.option('--sort-by', type=click.Choice(['name', 'state', 'speed', 'mac', 'vendor', 'ip']), 
              default=DEFAULT_SORT_BY, help=f'Sort by column (default: {DEFAULT_SORT_BY})')
@click.option('--color-scheme', type=click.Choice(['default', 'dark', 'light', 'high_contrast', 'colorblind']), 
              default=DEFAULT_COLOR_SCHEME, help='Color scheme to use')
def main(show_ipv6, no_vendors, include_virtual, show_summary, sort_by, color_scheme):
    """
    NetGrid: Display up-to-date network interface information in a table.
    """
    # Initialize color manager
    try:
        scheme = ColorScheme(color_scheme)
        color_manager = ColorManager(scheme)
    except ValueError:
        click.echo(ERROR_INVALID_COLOR_SCHEME.format(scheme=color_scheme))
        return
    
    # Initialize interface collector with vendor lookup toggle
    try:
        collector = InterfaceCollector(enable_vendor_lookup=not no_vendors)
    except Exception as e:
        click.echo(ERROR_INIT_COLLECTOR.format(error=e))
        return
    
    # Initialize table formatter
    formatter = TableFormatter()
    
    try:
        # Collect up-to-date interface data
        interfaces = collector.get_all_interfaces()
        
        # Filter out unwanted interfaces (unless include_virtual is specified)
        if include_virtual:
            filtered = interfaces
        else:
            filtered = [iface for iface in interfaces if not _is_virtual_interface(iface.name)]
        
        if not filtered:
            click.echo(ERROR_NO_INTERFACES)
            return
        
        # Display the table using the formatter
        formatter.print_table(
            interfaces=filtered,
            show_vendors=not no_vendors,
            show_ipv6=show_ipv6,
            show_summary=show_summary,
            sort_by=sort_by
        )
        
    except Exception as e:
        click.echo(ERROR_DISPLAY_INTERFACES.format(error=e))
        return

if __name__ == "__main__":
    main() 