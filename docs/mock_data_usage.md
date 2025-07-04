# NetGrid Mock Data Usage Guide

This guide explains how to use NetGrid's mock data functionality for testing in isolated environments like containers, CI/CD pipelines, or development environments where real network interfaces may not be available.

## Overview

NetGrid includes a comprehensive mock data system that provides realistic network interface data for testing purposes. This allows you to:

- Test NetGrid in containers without network access
- Run consistent tests in CI/CD environments
- Develop and debug without requiring specific network configurations
- Demonstrate NetGrid functionality in isolated environments

## Quick Start

### Enable Mock Mode

The simplest way to enable mock mode is through an environment variable:

```bash
export NETGRID_MOCK_MODE=1
netgrid
```

Or run it inline:

```bash
NETGRID_MOCK_MODE=1 netgrid
```

This will display a realistic set of mock network interfaces instead of querying the actual system.

### Using in Containers

Mock mode is particularly useful in containers:

```dockerfile
FROM python:3.9-slim

# Install NetGrid
COPY . /app
WORKDIR /app
RUN pip install -e .

# Enable mock mode for container usage
ENV NETGRID_MOCK_MODE=1

# Run NetGrid
CMD ["netgrid"]
```

## Configuration Options

### Environment Variables

NetGrid mock mode supports several environment variables for configuration:

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `NETGRID_MOCK_MODE` | `1`, `true`, `yes`, `on` (case-insensitive) | `false` | Enable/disable mock mode |
| `NETGRID_MOCK_INCLUDE_VIRTUAL` | `1`, `true`, `yes`, `on` | `true` | Include virtual interfaces (bonds, bridges, VLANs) |
| `NETGRID_MOCK_INCLUDE_FILTERED` | `1`, `true`, `yes`, `on` | `false` | Include normally filtered interfaces (veth, br-, tailscale) |

### Example Configurations

1. **Basic mock mode** (physical interfaces only):
   ```bash
   export NETGRID_MOCK_MODE=1
   export NETGRID_MOCK_INCLUDE_VIRTUAL=false
   netgrid
   ```

2. **Full mock mode** (includes all interface types):
   ```bash
   export NETGRID_MOCK_MODE=1
   export NETGRID_MOCK_INCLUDE_VIRTUAL=true
   export NETGRID_MOCK_INCLUDE_FILTERED=true
   netgrid
   ```

3. **Container testing** (includes Docker-style interfaces):
   ```bash
   NETGRID_MOCK_MODE=1 NETGRID_MOCK_INCLUDE_FILTERED=true netgrid
   ```

## Mock Data Contents

The mock data includes realistic examples of various interface types:

### Physical Interfaces
- `eth0` - Primary Ethernet (Gigabit, UP, with IPv4/IPv6)
- `eth1` - Secondary Ethernet (100 Mbps, UP)
- `enp0s3` - Systemd-named Ethernet (Gigabit, UP)
- `enp0s8` - Disconnected Ethernet (DOWN, no IP)

### Wireless Interfaces
- `wlan0` - Wireless interface (54 Mbps, UP, with IP)

### Virtual Interfaces
- `bond0` - Bonded interface (2 Gbps, UP)
- `br0` - Bridge interface (UP, with IP)
- `eth0.100` - VLAN interface (VLAN 100)
- `tun0` - VPN tunnel interface

### Special Interfaces
- `lo` - Loopback interface (always included)

### Filtered Interfaces (optional)
- `veth0abc123` - Docker veth interface
- `br-docker0` - Docker bridge
- `tailscale0` - Tailscale VPN interface

## Programmatic Usage

### Basic Mock Mode

```python
from netgrid.core.interface_collector import InterfaceCollector

# Enable mock mode programmatically
collector = InterfaceCollector(use_mock_data=True)
interfaces = collector.get_all_interfaces()

for interface in interfaces:
    print(f"{interface.name}: {interface.link_state.value}")
```

### Custom Mock Configuration

```python
from netgrid.core.mock_data_provider import MockDataProvider

# Custom provider configuration
provider = MockDataProvider(
    include_virtual=True,
    include_filtered=False
)

interfaces = provider.get_mock_interfaces()
print(f"Generated {len(interfaces)} mock interfaces")
```

### Creating Custom Interfaces

```python
from netgrid.core.mock_data_provider import MockDataProvider
from netgrid.core.data_models import InterfaceType, LinkState

# Create a custom mock interface
custom_interface = MockDataProvider.create_custom_interface(
    name="custom-eth0",
    ip_addresses=["10.0.0.100", "fe80::1"],
    speed=10000,
    interface_type=InterfaceType.PHYSICAL,
    vendor="Custom Corporation",
    link_state=LinkState.UP
)

print(f"Created: {custom_interface.name} ({custom_interface.vendor})")
```

## Testing with Mock Data

### Unit Tests

Mock data is particularly useful for unit tests:

```python
import pytest
from netgrid.core.interface_collector import InterfaceCollector

def test_interface_collection_with_mock_data():
    collector = InterfaceCollector(use_mock_data=True)
    interfaces = collector.get_all_interfaces()
    
    # Test that we have expected interfaces
    assert len(interfaces) > 0
    
    names = [iface.name for iface in interfaces]
    assert "eth0" in names
    assert "lo" in names

def test_specific_interface_details():
    collector = InterfaceCollector(use_mock_data=True)
    eth0 = collector.get_interface_details("eth0")
    
    assert eth0 is not None
    assert eth0.name == "eth0"
    assert eth0.interface_type == InterfaceType.PHYSICAL
    assert eth0.is_up
```

### CI/CD Integration

Mock mode enables consistent testing in CI environments:

```yaml
# GitHub Actions example
- name: Test NetGrid with mock data
  run: |
    export NETGRID_MOCK_MODE=1
    python -m pytest tests/
    
    # Test CLI output
    netgrid --show-summary
  env:
    NETGRID_MOCK_MODE: 1
    NETGRID_MOCK_INCLUDE_VIRTUAL: true
```

## Use Cases

### 1. Container Development

When developing or testing applications that use NetGrid in containers:

```bash
# Test in Alpine container
docker run --rm -it alpine:latest sh -c '
  apk add python3 py3-pip
  pip install netgrid
  NETGRID_MOCK_MODE=1 netgrid
'
```

### 2. Documentation and Demos

For generating consistent documentation screenshots or demos:

```bash
# Always shows the same interfaces for consistency
NETGRID_MOCK_MODE=1 netgrid --show-vendors --show-ipv6
```

### 3. Integration Testing

When testing applications that depend on NetGrid:

```python
import os
os.environ['NETGRID_MOCK_MODE'] = '1'

# Your application code that uses NetGrid
from netgrid import get_all_interfaces
interfaces = get_all_interfaces()
# ... test your logic with predictable interface data
```

### 4. Educational Use

For teaching network concepts without requiring specific hardware:

```bash
# Show different types of network interfaces
NETGRID_MOCK_MODE=1 NETGRID_MOCK_INCLUDE_VIRTUAL=true netgrid
```

## Mock Data Validation

The mock data is designed to be realistic and comprehensive:

- **MAC addresses**: Use locally administered prefixes (02:xx:xx:xx:xx:xx)
- **IP addresses**: Include both IPv4 and IPv6 where appropriate
- **Interface types**: Cover all major types (physical, wireless, virtual, etc.)
- **Vendors**: Include realistic vendor names from OUI database
- **States**: Mix of UP/DOWN interfaces for realistic scenarios
- **Speeds**: Various speeds from 54 Mbps (WiFi) to 10 Gbps
- **Flags**: Realistic interface flags (UP, BROADCAST, RUNNING, etc.)

## Troubleshooting

### Mock Mode Not Working

1. **Check environment variable**:
   ```bash
   echo $NETGRID_MOCK_MODE
   ```

2. **Verify programmatic setting**:
   ```python
   from netgrid.core.mock_data_provider import MockDataProvider
   print(MockDataProvider.is_mock_mode_enabled())
   ```

3. **Debug output**: Mock mode prints a message when enabled:
   ```
   NetGrid: Using mock data for testing
   ```

### No Interfaces Shown

If mock mode is enabled but no interfaces appear:

1. Check if virtual interfaces are excluded:
   ```bash
   export NETGRID_MOCK_INCLUDE_VIRTUAL=true
   ```

2. Verify the filtering logic in your application matches the mock data.

### Missing Interface Types

To include specific interface types:

```bash
# Include Docker/container interfaces
export NETGRID_MOCK_INCLUDE_FILTERED=true

# Include bond/bridge interfaces  
export NETGRID_MOCK_INCLUDE_VIRTUAL=true
```

## Advanced Usage

### Custom Mock Data Files

For advanced use cases, you can extend the MockDataProvider:

```python
from netgrid.core.mock_data_provider import MockDataProvider
from netgrid.core.data_models import NetworkInterface, InterfaceType, LinkState

class CustomMockProvider(MockDataProvider):
    def get_mock_interfaces(self):
        # Load custom interface data from file, database, etc.
        # Return InterfaceCollection with your custom data
        pass

# Use your custom provider
collector = InterfaceCollector(use_mock_data=True)
collector._mock_data_provider = CustomMockProvider()
```

### Environment-Specific Mock Data

You can create different mock datasets for different environments:

```python
import os
from netgrid.core.mock_data_provider import MockDataProvider

env = os.getenv('TEST_ENVIRONMENT', 'default')

if env == 'container':
    provider = MockDataProvider(include_filtered=True)
elif env == 'minimal':
    provider = MockDataProvider(include_virtual=False)
else:
    provider = MockDataProvider()

interfaces = provider.get_mock_interfaces()
```

## Best Practices

1. **Use mock mode for testing**: Always enable mock mode in test environments
2. **Consistent environments**: Use the same mock configuration across development and CI
3. **Document expectations**: Clearly document which mock interfaces your tests expect
4. **Validate assumptions**: Don't assume specific interfaces exist in production
5. **Environment detection**: Automatically enable mock mode in known isolated environments

## Conclusion

NetGrid's mock data system provides a robust foundation for testing and development in isolated environments. By using realistic interface data, you can ensure your applications work correctly without requiring specific network configurations or hardware.