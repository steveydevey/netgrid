# NetGrid

A command line tool to provide users with a visual table of information about network interfaces attached to the system, including link state, IP address(es), MAC address, speed, vendor information, and more.

## Features

- **Real-time Interface Discovery**: Live system queries using `/sys`, `/proc`, and system tools
- **Comprehensive Interface Information**: Display link state, IP addresses, MAC addresses, speed, MTU, driver info, vendor (with OUI lookup and caching), and more
- **Smart Filtering**: Automatically filters out virtual interfaces (veth, br-, lo, tailscale, etc.)
- **Beautiful Output**: Clean, readable table format with proper alignment and color
- **Vendor Lookup with Caching**: MAC address vendor information is fetched using public OUI APIs and cached locally for performance and offline use
- **Customizable Output**: Options for color scheme, summary, and disabling vendor lookups
- **Future-Ready**: Architecture designed to support real-time ncurses-style updates

## Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/yourusername/netgrid.git
cd netgrid
python3 -m venv venv
venv/bin/pip install uv
venv/bin/uv pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Basic Usage

```bash
# Display all network interfaces (filtered)
netgrid

# The tool automatically:
# - Collects real-time data from the system
# - Filters out virtual interfaces (veth, br-, lo, tailscale, etc.)
# - Shows interface name, state, speed, MAC, vendor, and IP addresses
```

### Example Output

```
Name            State    Speed      MAC                  Vendor           IP Addresses
-------------------------------------------------------------------------------
eno1            up       1Gbps      C4:34:6B:BA:79:6C    Hewlett Packard  192.168.254.77, fe80::c634:6bff:feba:796c
eno2            up       1Gbps      C4:34:6B:BA:79:6D    Hewlett Packard  fe80::c634:6bff:feba:796d
ens1f0          up       10Gbps     A0:36:9F:B3:06:54    Intel Corporate  192.168.254.132, fe80::a236:9fff:feb3:654
ens1f1          up       10Gbps     A0:36:9F:B3:06:55    Intel Corporate  fe80::a236:9fff:feb3:655
eno3            up       1Gbps      C4:34:6B:BA:79:6E    Hewlett Packard  -
eno4            down     -          C4:34:6B:BA:79:6F    Hewlett Packard  -
```

## Vendor Lookup and Caching

NetGrid uses public OUI APIs to look up the vendor for each MAC address. Results are cached locally in `~/.netgrid/cache` for performance and offline use. If a vendor cannot be found, the field will show `-`.

- To disable vendor lookups (for speed or privacy), use the `--no-vendors` option:

```bash
netgrid --no-vendors
```

## Customization and CLI Options

- `--show-ipv6` — Show IPv6 addresses in addition to IPv4
- `--no-vendors` — Disable vendor lookup (faster, no external requests)
- `--show-summary` — Show a summary of interface counts and types
- `--color-scheme` — Choose a color scheme: `default`, `dark`, `light`, `high_contrast`, `colorblind`

## Project Structure

```
netgrid/
├── src/netgrid/           # Source code
│   ├── core/              # Core business logic
│   │   ├── data_models.py           # Data structures and models
│   │   ├── interface_collector.py   # System interface discovery
│   │   └── vendor_lookup.py         # Vendor lookup and caching
│   ├── display/           # Output formatting
│   │   ├── table_formatter.py       # Table formatting and styling
│   │   └── color_manager.py         # Color schemes and themes
│   ├── utils/             # Utility functions
│   │   └── cache_manager.py         # Local cache management
│   └── cli/               # Command line interface
│       └── main.py        # CLI entry point
├── docs/                  # Documentation
├── tests/                 # Test suite
├── plans/                 # Project planning documents
└── requirements.txt       # Python dependencies
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/netgrid.git
cd netgrid

# Create virtual environment and install dependencies
python3 -m venv venv
venv/bin/pip install uv
venv/bin/uv pip install -e .[dev]

# Run tests
venv/bin/python -m pytest

# Format code
venv/bin/black src/ tests/

# Lint code
venv/bin/flake8 src/ tests/
```

### Running Tests

```bash
# Run all tests
venv/bin/python -m pytest

# Run with coverage
venv/bin/python -m pytest --cov=src

# Run specific test file
venv/bin/python -m pytest tests/core/test_vendor_lookup.py -v
```

## Documentation

- [Installation Guide](docs/user_guide/installation.md)
- [Usage Guide](docs/user_guide/usage.md)
- [Configuration](docs/user_guide/configuration.md)
- [Examples](docs/user_guide/examples.md)
- [Troubleshooting](docs/user_guide/troubleshooting.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/developer/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

### Phase 1: Basic Command Line Tool ✅ (In Progress)
- [x] Project planning and structure setup
- [x] Network interface discovery and data collection
- [x] Real-time system queries (no text files)
- [x] Basic CLI interface with filtering
- [x] Speed information display
- [x] Vendor lookup system with caching
- [x] Enhanced table formatting with colors
- [x] Additional CLI options and filtering

### Phase 2: Real-time Updates (Future)
- [ ] Ncurses interface
- [ ] Real-time monitoring
- [ ] Interactive controls
- [ ] Performance metrics

## Current Status

**Phase 1 - Complete** ✅
- ✅ Basic CLI tool is functional and displays real-time interface information
- ✅ System interface discovery and data collection working
- ✅ Speed information included in table output
- ✅ Interface filtering implemented (excludes veth, br-, lo, tailscale, vmsgohere)
- ✅ Vendor lookup and caching implemented
- ✅ Enhanced table formatting and color options
- ✅ CLI summary and color scheme options
- ✅ Comprehensive test suite in place
- ✅ Project structure and documentation established

**Next Priority**: Begin Phase 2 (real-time updates)

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/netgrid/issues)
- **Documentation**: [Project Docs](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/netgrid/discussions)

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Uses [psutil](https://github.com/giampaolo/psutil) for system information
- Uses [macvendors.com](https://macvendors.com/) and [macvendors.co](https://macvendors.co/) for OUI lookups
- Inspired by network monitoring tools like `ip`, `ifconfig`, and `netstat` 