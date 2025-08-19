# NetGrid Go

A high-performance Go implementation of NetGrid for displaying network interface information in a table format.

## Features

- **Real-time network interface discovery** using system tools
- **Vendor lookup** with caching (planned)
- **Colored output** with multiple themes
- **Sorting and filtering** options
- **IPv6 support**
- **Virtual interface filtering**
- **High performance** compared to Python version
- **Docker-based builds** (no Go installation required)

## Project Structure

```
netgrid-go/
├── cmd/                    # CLI commands using Cobra
│   └── root.go            # Main CLI entry point
├── internal/              # Internal packages
│   ├── collector/         # Network interface collection
│   │   └── collector.go   # Interface discovery logic
│   ├── display/           # Output formatting
│   │   └── table.go       # Table display functionality
│   └── models/            # Data models
│       └── interface.go   # Network interface data structures
├── main.go                # Application entry point
├── go.mod                 # Go module definition
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Docker services for build/run
├── Makefile               # Build and test commands
└── README.md              # This file
```

## Development Status

This is a work-in-progress Go implementation of NetGrid. Currently implemented:

- ✅ Basic CLI structure with Cobra
- ✅ Network interface data models
- ✅ Interface discovery using `ip -j addr show`
- ✅ Table formatting with colors
- ✅ Sorting functionality
- ✅ Virtual interface filtering
- ✅ Docker-based build system

### Planned Features

- 🔄 Vendor lookup with OUI database
- 🔄 Speed/duplex detection using ethtool
- 🔄 DHCP/static IP configuration detection
- 🔄 Performance benchmarking vs Python version
- 🔄 Additional CLI options and themes

## Building

### Option 1: Docker-based Build (Recommended - No Go Required)

```bash
# Build the application using Docker
make docker-build

# Run the application in Docker
make docker-run

# Extract binary to local filesystem
make extract-binary
./bin/netgrid-go
```

### Option 2: Local Go Build (Requires Go Installation)

```bash
# Install Go dependencies
go mod tidy

# Build the application
go build -o netgrid-go .

# Run the application
./netgrid-go
```

## Docker Commands

```bash
# Build the application
docker-compose run --rm build

# Run the application
docker-compose --profile runtime run --rm netgrid-go

# Start development shell with Go environment
docker-compose --profile dev run --rm dev

# Run with specific options
docker-compose --profile runtime run --rm netgrid-go --show-ipv6
docker-compose --profile runtime run --rm netgrid-go --include-virtual
docker-compose --profile runtime run --rm netgrid-go --sort-by speed
```

## Usage

```bash
# Basic usage
./netgrid-go

# Show IPv6 addresses
./netgrid-go --show-ipv6

# Disable vendor lookup
./netgrid-go --no-vendors

# Include virtual interfaces
./netgrid-go --include-virtual

# Sort by different columns
./netgrid-go --sort-by speed
./netgrid-go --sort-by mac
./netgrid-go --sort-by state

# Show summary
./netgrid-go --show-summary

# Different color schemes
./netgrid-go --color-scheme dark
./netgrid-go --color-scheme light
```

## Makefile Targets

```bash
# Show all available commands
make help

# Docker-based commands (no Go required)
make docker-build      # Build using Docker
make docker-run        # Run in Docker container
make docker-dev        # Start development shell
make extract-binary    # Build and extract binary locally

# Local commands (requires Go)
make build             # Build locally
make run               # Build and run locally
make test              # Run tests
make fmt               # Format code
make lint              # Lint code

# Cleanup
make clean             # Clean build artifacts
make docker-clean      # Clean Docker artifacts
```

## Performance Goals

The Go implementation aims to provide:

- **Faster startup time** compared to Python
- **Lower memory usage** 
- **Single binary distribution** (no Python runtime required)
- **Better performance** for large numbers of interfaces
- **Docker-based builds** for consistent environments

## Comparison with Python Version

| Feature | Python | Go | Status |
|---------|--------|----|--------|
| Interface Discovery | ✅ | ✅ | Complete |
| Table Formatting | ✅ | ✅ | Complete |
| Sorting | ✅ | ✅ | Complete |
| Virtual Filtering | ✅ | ✅ | Complete |
| Docker Builds | 🔄 | ✅ | Complete |
| Vendor Lookup | ✅ | 🔄 | In Progress |
| Speed Detection | ✅ | 🔄 | Planned |
| IP Config Detection | ✅ | 🔄 | Planned |
| Performance | Baseline | TBD | To Benchmark |

## Docker Architecture

The Docker setup uses a multi-stage build:

1. **Builder Stage**: Uses `golang:1.21-alpine` to compile the application
2. **Runtime Stage**: Uses minimal `alpine:latest` with only required dependencies
3. **Host Network Access**: Container runs with `network_mode: host` to access network interfaces
4. **Security**: Runs as non-root user for better security

## Contributing

This is an experimental Go rewrite of the Python NetGrid project. Contributions are welcome!

## License

Same as the main NetGrid project. 