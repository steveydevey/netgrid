# NetGrid Go Makefile

.PHONY: build clean test run help docker-build docker-run docker-dev docker-clean

# Binary name
BINARY_NAME=netgrid-go

# Build the application (requires Go installed)
build:
	@echo "Building NetGrid Go..."
	go mod tidy
	go build -o $(BINARY_NAME) .

# Build using Docker (no Go installation required)
docker-build:
	@echo "Building NetGrid Go using Docker..."
	@mkdir -p bin
	docker-compose run --rm build

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(BINARY_NAME)
	rm -rf bin/
	go clean

# Clean Docker artifacts
docker-clean:
	@echo "Cleaning Docker artifacts..."
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

# Run tests
test:
	@echo "Running tests..."
	go test ./...

# Run the application (requires Go)
run: build
	@echo "Running NetGrid Go..."
	./$(BINARY_NAME)

# Run using Docker container
docker-run:
	@echo "Running NetGrid Go in Docker..."
	docker-compose --profile runtime run --rm netgrid-go

# Run with specific flags using Docker
docker-run-ipv6:
	docker-compose --profile runtime run --rm netgrid-go --show-ipv6

docker-run-virtual:
	docker-compose --profile runtime run --rm netgrid-go --include-virtual

docker-run-sort-speed:
	docker-compose --profile runtime run --rm netgrid-go --sort-by speed

# Development shell with Go environment
docker-dev:
	@echo "Starting development shell..."
	docker-compose --profile dev run --rm dev

# Install dependencies
deps:
	@echo "Installing dependencies..."
	go mod download

# Format code
fmt:
	@echo "Formatting code..."
	go fmt ./...

# Lint code
lint:
	@echo "Linting code..."
	golangci-lint run

# Build and extract binary from Docker
extract-binary: docker-build
	@echo "Binary extracted to bin/netgrid-go"
	@echo "You can now run: ./bin/netgrid-go"

# Show help
help:
	@echo "Available targets:"
	@echo ""
	@echo "Local development (requires Go):"
	@echo "  build        - Build the application"
	@echo "  run          - Build and run the application"
	@echo "  test         - Run tests"
	@echo "  deps         - Install dependencies"
	@echo "  fmt          - Format code"
	@echo "  lint         - Lint code"
	@echo ""
	@echo "Docker-based (no Go required):"
	@echo "  docker-build - Build using Docker"
	@echo "  docker-run   - Run in Docker container"
	@echo "  docker-dev   - Start development shell"
	@echo "  docker-run-ipv6     - Run with IPv6 addresses"
	@echo "  docker-run-virtual  - Run with virtual interfaces"
	@echo "  docker-run-sort-speed - Run sorted by speed"
	@echo "  extract-binary - Build and extract binary locally"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean        - Clean build artifacts"
	@echo "  docker-clean - Clean Docker artifacts"
	@echo "  help         - Show this help"

# Default target
.DEFAULT_GOAL := help 