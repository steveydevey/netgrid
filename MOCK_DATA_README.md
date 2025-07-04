# NetGrid Mock Data Implementation

This implementation adds comprehensive mock data support to NetGrid for testing in isolated environments like containers.

## What Was Implemented

### 1. MockDataProvider (`src/netgrid/core/mock_data_provider.py`)
- Comprehensive mock data generator with realistic network interface data
- Supports 10+ different interface types (physical, wireless, virtual, etc.)
- Configurable inclusion/exclusion of virtual and filtered interfaces
- Environment variable configuration support
- Custom interface creation capabilities
- Realistic MAC addresses, IP addresses, speeds, and vendor information

### 2. Enhanced InterfaceCollector (`src/netgrid/core/interface_collector.py`)
- Added mock mode detection and integration
- Automatic fallback to mock data when `NETGRID_MOCK_MODE=1`
- Preserves all existing functionality for real system data
- Seamless switching between real and mock data sources

### 3. Comprehensive Test Suite (`tests/core/test_mock_data_provider.py`)
- Unit tests for all mock data functionality
- Environment variable testing
- Integration tests with InterfaceCollector
- Data validation and realism tests

### 4. Documentation (`docs/mock_data_usage.md`)
- Complete usage guide with examples
- Container integration instructions
- Troubleshooting guide
- Best practices for testing

### 5. Demo Scripts
- `scripts/simple_mock_demo.py` - Standalone demonstration
- `scripts/demo_mock_mode.py` - Full integration demo (requires dependencies)

## Key Features

### Environment Variables
- `NETGRID_MOCK_MODE=1` - Enable mock mode
- `NETGRID_MOCK_INCLUDE_VIRTUAL=true/false` - Include virtual interfaces
- `NETGRID_MOCK_INCLUDE_FILTERED=true/false` - Include normally filtered interfaces

### Mock Interface Types
- **Physical**: eth0, eth1, enp0s3, enp0s8 (UP/DOWN examples)
- **Wireless**: wlan0 (54 Mbps)
- **Virtual**: bond0 (2 Gbps), br0 (bridge), eth0.100 (VLAN), tun0 (VPN)
- **Special**: lo (loopback)
- **Filtered**: veth0abc123, br-docker0, tailscale0 (optional)

### Realistic Data
- Valid MAC addresses with locally administered prefixes
- Mixed IPv4 and IPv6 addresses
- Realistic speeds (54 Mbps to 10 Gbps)
- Authentic vendor names (Intel Corporation, Red Hat Inc.)
- Proper interface flags and states

## Usage Examples

### Basic Usage
```bash
export NETGRID_MOCK_MODE=1
netgrid
```

### Container Usage
```dockerfile
ENV NETGRID_MOCK_MODE=1
RUN netgrid
```

### Programmatic Usage
```python
from netgrid.core.interface_collector import InterfaceCollector

collector = InterfaceCollector(use_mock_data=True)
interfaces = collector.get_all_interfaces()
```

### Custom Configuration
```bash
NETGRID_MOCK_MODE=1 \
NETGRID_MOCK_INCLUDE_VIRTUAL=true \
NETGRID_MOCK_INCLUDE_FILTERED=true \
netgrid
```

## Testing

Run the demo to see mock functionality:
```bash
python3 scripts/simple_mock_demo.py
```

The demo shows:
- 10 realistic mock interfaces
- Different configuration options
- Environment variable handling
- Custom interface creation
- Data validation and realism

## Integration with NetGrid

The mock system integrates seamlessly with existing NetGrid functionality:

1. **Automatic Detection**: When `NETGRID_MOCK_MODE=1` is set, the InterfaceCollector automatically uses mock data
2. **Transparent API**: All existing code works unchanged - mock data is returned through the same interfaces
3. **Vendor Lookup**: Mock data includes realistic vendor information, compatible with the vendor lookup system
4. **Filtering**: The CLI's interface filtering (veth, br-, lo, tailscale) works correctly with mock data

## Benefits

1. **Container Testing**: Test NetGrid in isolated environments without network access
2. **Consistent CI/CD**: Predictable interface data for automated testing
3. **Development**: Develop and debug without specific network configurations
4. **Documentation**: Generate consistent screenshots and examples
5. **Education**: Demonstrate network concepts without hardware requirements

## Files Modified/Added

### New Files
- `src/netgrid/core/mock_data_provider.py` - Core mock functionality
- `tests/core/test_mock_data_provider.py` - Comprehensive test suite
- `docs/mock_data_usage.md` - Usage documentation
- `scripts/simple_mock_demo.py` - Standalone demo
- `scripts/demo_mock_mode.py` - Full demo (requires dependencies)

### Modified Files
- `src/netgrid/core/interface_collector.py` - Added mock mode integration

## Demo Output Summary

The mock system generates realistic data including:
- 10 diverse interface types (physical, wireless, virtual, special)
- Mixed UP/DOWN states for realistic scenarios
- Speed range from 54 Mbps (WiFi) to 2000 Mbps (bonded)
- Proper vendor attribution (Intel Corporation, Red Hat Inc.)
- Valid MAC address formats
- IPv4 and IPv6 address assignments
- Realistic interface flags and properties

This implementation provides a robust foundation for testing NetGrid in any isolated environment while maintaining full compatibility with existing functionality.