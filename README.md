# NetGrid

A command line tool to provide users with a visual table of information about network interfaces attached to the system, including link state, IP address(es), MAC address, vendor information, and more.

## Features

- **Comprehensive Interface Information**: Display link state, IP addresses, MAC addresses, MTU, driver info, and more
- **Vendor Lookup**: Automatic vendor identification via OUI lookup with local caching
- **Beautiful Output**: Rich, color-coded tables with proper formatting
- **Flexible Filtering**: Filter interfaces by type, status, or custom criteria
- **Future-Ready**: Architecture designed to support real-time ncurses-style updates

## Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/yourusername/netgrid.git
cd netgrid
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Basic Usage

```bash
# Display all network interfaces
netgrid

# Show specific interface details
netgrid --interface eth0

# Filter interfaces by type
netgrid --filter physical

# Disable color output
netgrid --no-color
```

## Project Structure

```
netgrid/
├── src/                    # Source code
│   ├── core/              # Core business logic
│   ├── display/           # Output formatting
│   ├── utils/             # Utility functions
│   └── cli/               # Command line interface
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

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_interface_collector.py
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

### Phase 1: Basic Command Line Tool ✅
- [x] Project planning and structure
- [ ] Network interface discovery
- [ ] Data collection and formatting
- [ ] Vendor lookup system
- [ ] CLI interface

### Phase 2: Real-time Updates (Future)
- [ ] Ncurses interface
- [ ] Real-time monitoring
- [ ] Interactive controls
- [ ] Performance metrics

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/netgrid/issues)
- **Documentation**: [Project Docs](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/netgrid/discussions)

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Uses [psutil](https://github.com/giampaolo/psutil) for system information
- Inspired by network monitoring tools like `ip`, `ifconfig`, and `netstat` 