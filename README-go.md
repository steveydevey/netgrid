# NetGrid Go Version

A Go implementation of NetGrid with attractive output formatting similar to the Python version.

## Features

- **Beautiful Terminal Output**: Rich colors, styled tables, and professional formatting
- **Multiple Color Schemes**: 5 different schemes (default, dark, light, high_contrast, colorblind)
- **Comprehensive Interface Information**: Link state, IP addresses, MAC addresses, speed, vendor info
- **Smart Filtering**: Automatically filters out virtual interfaces unless requested
- **Flexible Sorting**: Sort by name, state, speed, MAC, vendor, or IP address
- **Summary Statistics**: Optional interface count and type breakdown

## Installation

```bash
# Clone the repository (if not already cloned)
git clone <repository-url>
cd netgrid

# Build the Go version
go build -o netgrid cmd/netgrid/main.go

# Or install directly
go install ./cmd/netgrid
```

## Usage

```bash
# Basic usage
./netgrid

# Show help
./netgrid --help

# Include IPv6 addresses
./netgrid --show-ipv6

# Include virtual interfaces
./netgrid --include-virtual

# Disable vendor lookup (faster)
./netgrid --no-vendors

# Show summary statistics
./netgrid --show-summary

# Use different color scheme
./netgrid --color-scheme dark

# Sort by different criteria
./netgrid --sort-by state
./netgrid --sort-by speed

# Combine options
./netgrid --show-ipv6 --show-summary --color-scheme high_contrast --sort-by state
```

## Available Options

### Color Schemes
- `default` - Standard colors for most terminals
- `dark` - Optimized for dark terminal backgrounds
- `light` - Optimized for light terminal backgrounds  
- `high_contrast` - High contrast for accessibility
- `colorblind` - Colorblind-friendly palette

### Sort Options
- `name` - Sort by interface name (default)
- `state` - Sort by state (UP interfaces first)
- `speed` - Sort by speed (highest first)
- `mac` - Sort by MAC address
- `vendor` - Sort by vendor name
- `ip` - Sort by IP address

## Output Features

The Go version produces attractive output with:

- **Colored Status Indicators**: Green/red bullets (●) for UP/DOWN states
- **Professional Table Borders**: Unicode box-drawing characters
- **Color-Coded Data**:
  - Green for IPv4 addresses
  - Cyan for IPv6 addresses
  - Blue for MAC addresses
  - Magenta for vendor names
  - Yellow for speed information
- **Smart Data Formatting**:
  - Speed displayed as "1Gbps", "100Mbps", etc.
  - Missing data shown as dimmed "-"
  - Proper alignment and spacing
- **Rich Title Banner**: Centered title with decorative borders
- **Summary Tables**: Interface statistics with colored counts

## Example Output

```
┌─────────────────────────────────────────┐
│               NetGrid                   │
│        Network Interface Information    │
└─────────────────────────────────────────┘

┌──────────────┬─────────┬───────────────────┬──────┬──────────┬─────────────────┬──────────────────────────────┐
│     NAME     │  SPEED  │        MAC        │ MTU  │ IP CONFIG│     VENDOR      │         IP ADDRESSES         │
├──────────────┼─────────┼───────────────────┼──────┼──────────┼─────────────────┼──────────────────────────────┤
│ ● eno1       │ 1Gbps   │ C4:34:6B:BA:79:6C │ 1500 │   DHCP   │ Hewlett Packard │ 192.168.1.100                │
│ ● eno2       │ 1Gbps   │ C4:34:6B:BA:79:6D │ 1500 │    -     │ Hewlett Packard │ -                            │
│ ● ens1f0     │ 10Gbps  │ A0:36:9F:B3:06:54 │ 1500 │  Static  │ Intel           │ 192.168.254.132              │
│ ● ens1f1     │ 10Gbps  │ A0:36:9F:B3:06:55 │ 1500 │    -     │ Intel           │ -                            │
└──────────────┴─────────┴───────────────────┴──────┴──────────┴─────────────────┴──────────────────────────────┘
```

## Architecture

The Go version follows a clean modular architecture:

```
netgrid/
├── cmd/netgrid/           # Main application entry point
│   └── main.go
├── internal/
│   ├── models/            # Data models and structures
│   │   └── interface.go
│   ├── collector/         # System interface collection
│   │   └── interface_collector.go
│   └── display/           # Output formatting and colors
│       ├── colors.go
│       └── formatter.go
├── go.mod                 # Go module definition
└── README-go.md          # This file
```

## Dependencies

- `github.com/fatih/color` - Terminal color support
- `github.com/olekukonko/tablewriter` - Table formatting
- `github.com/spf13/cobra` - CLI framework

## Comparison with Python Version

The Go version provides feature parity with the Python version:

✅ **Implemented Features:**
- Rich terminal output with colors and styling
- Multiple color schemes
- Professional table formatting
- Interface status indicators
- Vendor lookup (basic implementation)
- Virtual interface filtering
- Multiple sorting options
- Summary statistics
- Command-line options

🚧 **Future Enhancements:**
- Enhanced vendor lookup with OUI database
- Performance optimizations
- Additional output formats
- Configuration file support

## Performance

The Go version offers several performance advantages:
- Fast startup time
- Low memory usage
- Efficient system interface collection
- Single binary deployment