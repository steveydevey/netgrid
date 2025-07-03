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

## Installation

### Method 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/netgrid.git
cd netgrid

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
# OR
venv\Scripts\activate     # On Windows

# Install uv for faster package management
pip install uv

# Install NetGrid in development mode
uv pip install -e .
```

### Method 2: Quick Install with pip

```bash
# Create virtual environment (recommended)
python3 -m venv netgrid-env
source netgrid-env/bin/activate

# Install dependencies directly
pip install -r requirements.txt

# Run from source directory
python -m netgrid.cli.main
```

### Method 3: System-wide Installation

⚠️ **Warning**: Installing packages system-wide can cause conflicts. Virtual environments are recommended.

```bash
# Install dependencies system-wide
sudo pip install psutil netifaces requests rich click

# Clone and run
git clone https://github.com/yourusername/netgrid.git
cd netgrid
python -m netgrid.cli.main
```

## Requirements

- **Python**: 3.8 or newer
- **Operating System**: Linux (tested on Ubuntu, CentOS, Amazon Linux)
- **Privileges**: Some features may require root privileges for full system access
- **Network**: Internet connection for vendor lookup (optional)

## Quick Start

### Basic Usage

After installation, you can run NetGrid in several ways:

```bash
# If installed with setup.py (Method 1)
netgrid

# If running from source
python -m netgrid.cli.main

# Or directly from the main file
python src/netgrid/cli/main.py
```

### Command Line Options

NetGrid supports several command-line options to customize the output:

```bash
# Show all available options
netgrid --help

# Basic usage with different options
netgrid                              # Default output
netgrid --show-ipv6                  # Include IPv6 addresses
netgrid --no-vendors                 # Skip vendor lookup (faster)
netgrid --show-summary               # Show interface count summary
netgrid --color-scheme dark          # Use dark color scheme

# Combine options
netgrid --show-ipv6 --show-summary --color-scheme high_contrast
```

### Available Color Schemes

- `default` - Standard colors for most terminals
- `dark` - Optimized for dark terminal backgrounds
- `light` - Optimized for light terminal backgrounds  
- `high_contrast` - High contrast for accessibility
- `colorblind` - Colorblind-friendly palette

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

## Running Without Installation

You can run NetGrid directly from the source code without installing it:

```bash
# Clone the repository
git clone https://github.com/yourusername/netgrid.git
cd netgrid

# Install dependencies only
pip install psutil netifaces requests rich click

# Run directly
python -m netgrid.cli.main
# OR
python src/netgrid/cli/main.py
```

## Vendor Lookup and Caching

NetGrid uses public OUI APIs to look up the vendor for each MAC address. Results are cached locally in `~/.netgrid/cache` for performance and offline use.

### Vendor Lookup Behavior

- **First run**: Fetches vendor information from internet APIs
- **Subsequent runs**: Uses cached data for known MAC addresses
- **Cache location**: `~/.netgrid/cache/vendors.json`
- **Offline mode**: Works with cached data when internet is unavailable

### Performance Options

```bash
# Skip vendor lookup for faster execution
netgrid --no-vendors

# Clear vendor cache (force refresh)
rm -rf ~/.netgrid/cache
```

## Troubleshooting

### Common Issues

#### 1. "netgrid: command not found"

**Problem**: The `netgrid` command is not in your PATH.

**Solutions**:
```bash
# Option A: Activate the virtual environment
source venv/bin/activate
netgrid

# Option B: Run directly from source
python -m netgrid.cli.main

# Option C: Check if installed correctly
pip list | grep netgrid
```

#### 2. "Permission denied" or "No interfaces found"

**Problem**: Insufficient privileges to read system network information.

**Solutions**:
```bash
# Run with sudo (if needed)
sudo netgrid

# Or run with user privileges (limited info)
netgrid --no-vendors
```

#### 3. "Module not found" errors

**Problem**: Missing dependencies.

**Solutions**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific missing package
pip install psutil netifaces requests rich click
```

#### 4. Vendor lookup fails

**Problem**: Network issues or API rate limiting.

**Solutions**:
```bash
# Run without vendor lookup
netgrid --no-vendors

# Check internet connectivity
ping google.com

# Clear cache and retry
rm -rf ~/.netgrid/cache
netgrid
```

#### 5. "No network interfaces found"

**Problem**: All interfaces are being filtered out.

**Possible causes**:
- System only has virtual interfaces (Docker, VMs)
- Running in a container with limited network access
- Network interfaces have unusual naming

**Check what interfaces exist**:
```bash
# Check system interfaces
ip link show
# Or
ifconfig -a

# Run with verbose output (if available)
python -c "from netgrid.core.interface_collector import InterfaceCollector; print([i.name for i in InterfaceCollector().get_all_interfaces()])"
```

### System Compatibility

NetGrid is tested on:
- ✅ Ubuntu 18.04, 20.04, 22.04
- ✅ CentOS 7, 8
- ✅ Amazon Linux 2
- ✅ Debian 10, 11
- ⚠️ Alpine Linux (limited testing)
- ❌ Windows (not supported)
- ❌ macOS (not tested)

## Development

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/netgrid.git
cd netgrid

# Create development environment
python3 -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install uv
uv pip install -e .[dev]

# Verify installation
netgrid --help
```

### Running During Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run the tool
netgrid

# Or run directly from source (without installation)
python -m netgrid.cli.main

# Or run the main module directly
python src/netgrid/cli/main.py
```

### Development Commands

```bash
# Run tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run specific test
python -m pytest tests/core/test_interface_collector.py -v
```

### Project Structure

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

### Phase 1: Basic Command Line Tool ✅ (Complete)
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