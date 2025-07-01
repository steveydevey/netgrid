# NetGrid Source Code Structure

## Directory Layout

```
src/
├── __init__.py
├── core/                    # Core business logic
│   ├── __init__.py
│   ├── interface_collector.py
│   ├── vendor_lookup.py
│   └── data_models.py
├── display/                 # Output formatting and display
│   ├── __init__.py
│   ├── table_formatter.py
│   └── color_manager.py
├── utils/                   # Utility functions and helpers
│   ├── __init__.py
│   ├── system_utils.py
│   └── cache_manager.py
└── cli/                     # Command line interface
    ├── __init__.py
    └── main.py
```

## Module Details

### Core Module (`src/core/`)

#### `data_models.py`
**Purpose**: Define data structures for network interface information

**Classes**:
- `NetworkInterface`: Main data class for interface information
  - `name`: Interface name (str)
  - `mac_address`: MAC address (str)
  - `ip_addresses`: List of IP addresses (IPv4/IPv6)
  - `link_state`: Up/down status (str)
  - `speed`: Link speed in Mbps (int)
  - `duplex`: Full/half duplex (str)
  - `mtu`: MTU size (int)
  - `driver`: Driver name (str)
  - `vendor`: Vendor name from OUI lookup (str)
  - `interface_type`: Physical/virtual/loopback (str)

- `InterfaceCollection`: Container for multiple interfaces
  - `interfaces`: List of NetworkInterface objects
  - Methods for filtering, sorting, and searching

#### `interface_collector.py`
**Purpose**: Discover and collect network interface information

**Functions**:
- `get_all_interfaces()`: Return list of all network interfaces
- `get_interface_details(interface_name)`: Get detailed info for specific interface
- `get_ip_addresses(interface_name)`: Get all IP addresses for interface
- `get_link_state(interface_name)`: Get current link state
- `get_interface_stats(interface_name)`: Get performance statistics

**Dependencies**:
- `psutil` for system information
- `netifaces` for network interface data
- System file parsing (`/sys/class/net/`, `/proc/net/dev`)

#### `vendor_lookup.py`
**Purpose**: Handle MAC address to vendor name resolution

**Classes**:
- `VendorLookup`: Main vendor lookup class
  - `lookup_vendor(mac_address)`: Look up vendor for MAC address
  - `batch_lookup(mac_addresses)`: Look up multiple vendors efficiently
  - `update_cache()`: Update local cache from online sources

**Functions**:
- `extract_oui(mac_address)`: Extract OUI from MAC address
- `validate_mac_address(mac_address)`: Validate MAC address format

**Dependencies**:
- `requests` for HTTP lookups
- Local cache file for offline operation

### Display Module (`src/display/`)

#### `table_formatter.py`
**Purpose**: Format network interface data into tables

**Classes**:
- `InterfaceTable`: Main table formatting class
  - `format_table(interfaces)`: Create formatted table from interface data
  - `add_column(name, formatter)`: Add custom column with formatter
  - `set_sort_column(column, reverse=False)`: Set sorting preferences

**Functions**:
- `format_mac_address(mac)`: Format MAC address with separators
- `format_ip_addresses(ips)`: Format IP address list
- `format_speed(speed)`: Format speed with units (Mbps/Gbps)

#### `color_manager.py`
**Purpose**: Manage colors and themes for output

**Classes**:
- `ColorTheme`: Theme configuration class
  - `link_up_color`: Color for up interfaces
  - `link_down_color`: Color for down interfaces
  - `header_color`: Color for table headers
  - `vendor_color`: Color for vendor information

**Functions**:
- `apply_color(text, color)`: Apply color to text
- `get_status_color(status)`: Get appropriate color for link status

### Utils Module (`src/utils/`)

#### `system_utils.py`
**Purpose**: System-specific operations and utilities

**Functions**:
- `is_root_user()`: Check if running as root
- `get_system_info()`: Get basic system information
- `read_sys_file(path)`: Safely read system files
- `run_command(command)`: Execute system commands safely

#### `cache_manager.py`
**Purpose**: Manage local cache for vendor lookups

**Classes**:
- `VendorCache`: Cache management class
  - `get_cached_vendor(oui)`: Get vendor from cache
  - `cache_vendor(oui, vendor)`: Cache vendor information
  - `load_cache()`: Load cache from file
  - `save_cache()`: Save cache to file
  - `clear_cache()`: Clear all cached data

### CLI Module (`src/cli/`)

#### `main.py`
**Purpose**: Command line interface entry point

**Functions**:
- `main()`: Main CLI entry point
- `display_interfaces()`: Display interface table
- `display_single_interface(interface_name)`: Display single interface details

**CLI Options**:
- `--interfaces`: Filter specific interfaces
- `--format`: Output format (table, json, csv)
- `--no-color`: Disable color output
- `--sort-by`: Sort by specific column
- `--filter`: Filter interfaces by criteria

## Implementation Order

### Phase 1: Foundation (Week 1)
1. Create basic project structure
2. Implement `data_models.py` with core data structures
3. Create basic `interface_collector.py` with minimal functionality
4. Set up CLI framework with `main.py`

### Phase 2: Data Collection (Week 2)
1. Complete `interface_collector.py` implementation
2. Add comprehensive system utilities in `system_utils.py`
3. Implement basic table formatting in `table_formatter.py`
4. Add basic CLI functionality

### Phase 3: Vendor Lookup (Week 3)
1. Implement `vendor_lookup.py` with online lookup
2. Create `cache_manager.py` for local caching
3. Integrate vendor lookup with interface collection
4. Add offline fallback mechanisms

### Phase 4: Polish and Testing (Week 4)
1. Complete `color_manager.py` implementation
2. Enhance table formatting with colors and themes
3. Add comprehensive CLI options
4. Implement error handling and edge cases

## Code Standards

### Python Style
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Document all public functions and classes with docstrings
- Use f-strings for string formatting

### Error Handling
- Use custom exceptions for domain-specific errors
- Implement graceful degradation for system operations
- Provide meaningful error messages to users
- Log errors appropriately for debugging

### Testing Strategy
- Unit tests for each module
- Mock external dependencies (system calls, HTTP requests)
- Integration tests for data flow between modules
- System tests for end-to-end functionality

### Performance Considerations
- Cache vendor lookups to minimize HTTP requests
- Use efficient data structures for large interface lists
- Minimize system calls by batching operations
- Implement lazy loading where appropriate

## Dependencies

### Required Packages
```
psutil>=5.8.0          # System and process utilities
netifaces>=0.11.0      # Network interface information
requests>=2.25.0       # HTTP requests for vendor lookup
rich>=12.0.0           # Rich text and table formatting
click>=8.0.0           # Command line interface creation
```

### Development Dependencies
```
pytest>=6.0.0          # Testing framework
pytest-cov>=2.12.0     # Coverage reporting
black>=21.0.0          # Code formatting
flake8>=3.9.0          # Linting
mypy>=0.910            # Type checking
```

## Configuration

### User Configuration
- Cache directory location
- Default output format
- Color theme preferences
- Update intervals for real-time mode

### System Configuration
- Vendor lookup API endpoints
- Cache expiration times
- System file paths for different distributions
- Permission requirements for various operations 