package collector

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"strings"
	"strconv"

	"github.com/netgrid/netgrid-go/internal/models"
)

// InterfaceCollector collects network interface information from the system
type InterfaceCollector struct {
	enableVendorLookup bool
	ipConfigCache      map[string]models.IPConfigType
}

// NewInterfaceCollector creates a new interface collector
func NewInterfaceCollector(enableVendorLookup bool) *InterfaceCollector {
	return &InterfaceCollector{
		enableVendorLookup: enableVendorLookup,
		ipConfigCache:      make(map[string]models.IPConfigType),
	}
}

// GetAllInterfaces discovers and returns all network interfaces
func (ic *InterfaceCollector) GetAllInterfaces() (*models.InterfaceCollection, error) {
	collection := models.NewInterfaceCollection()
	
	// Get interface data using 'ip -j addr show'
	interfaces, err := ic.discoverInterfaces()
	if err != nil {
		return collection, fmt.Errorf("failed to discover interfaces: %w", err)
	}
	
	// Add interfaces to collection
	for _, iface := range interfaces {
		collection.AddInterface(iface)
	}
	
	// TODO: Add vendor lookup if enabled
	// TODO: Add speed/duplex information using ethtool
	
	return collection, nil
}

// discoverInterfaces discovers interfaces using 'ip -j addr show'
func (ic *InterfaceCollector) discoverInterfaces() ([]*models.NetworkInterface, error) {
	cmd := exec.Command("ip", "-j", "addr", "show")
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to run 'ip -j addr show': %w", err)
	}
	
	var ipData []map[string]interface{}
	if err := json.Unmarshal(output, &ipData); err != nil {
		return nil, fmt.Errorf("failed to parse ip command output: %w", err)
	}
	
	var interfaces []*models.NetworkInterface
	
	for _, data := range ipData {
		iface, err := ic.parseInterfaceData(data)
		if err != nil {
			// Log error but continue with other interfaces
			fmt.Printf("Warning: failed to parse interface data: %v\n", err)
			continue
		}
		interfaces = append(interfaces, iface)
	}
	
	return interfaces, nil
}

// parseInterfaceData parses a single interface from the ip command output
func (ic *InterfaceCollector) parseInterfaceData(data map[string]interface{}) (*models.NetworkInterface, error) {
	// Extract basic information
	name, ok := data["ifname"].(string)
	if !ok || name == "" {
		return nil, fmt.Errorf("invalid or missing interface name")
	}
	
	macAddress, _ := data["address"].(string)
	
	// Determine state
	operstate, _ := data["operstate"].(string)
	linkState := ic.parseLinkState(operstate)
	isUp := linkState == models.LinkStateUP
	
	// Extract IP addresses (only for UP interfaces)
	var ipAddresses []string
	ipConfigType := models.IPConfigUnknown
	if isUp {
		if addrInfo, ok := data["addr_info"].([]interface{}); ok {
			for _, addr := range addrInfo {
				if addrMap, ok := addr.(map[string]interface{}); ok {
					if local, ok := addrMap["local"].(string); ok {
						ipAddresses = append(ipAddresses, local)
					}
				}
			}
		}
		ipConfigType = ic.detectIPConfigType(name)
	}
	
	// Extract MTU
	var mtu *int
	if mtuStr, ok := data["mtu"].(float64); ok {
		mtuInt := int(mtuStr)
		mtu = &mtuInt
	}
	
	// Extract flags
	var flags []string
	if flagsData, ok := data["flags"].([]interface{}); ok {
		for _, flag := range flagsData {
			if flagStr, ok := flag.(string); ok {
				flags = append(flags, flagStr)
			}
		}
	}
	
	// Determine interface type
	interfaceType := ic.determineInterfaceType(name)
	
	// Create the interface
	iface := &models.NetworkInterface{
		Name:          name,
		LinkState:     linkState,
		MACAddress:    macAddress,
		IPAddresses:   ipAddresses,
		MTU:           mtu,
		InterfaceType: interfaceType,
		IPConfigType:  ipConfigType,
		Flags:         flags,
		Duplex:        models.DuplexModeUNKNOWN,
		ExtraData:     make(map[string]interface{}),
	}
	
	// Normalize MAC address
	iface.NormalizeMACAddress()

	// --- SPEED COLLECTION ---
	speed, err := getInterfaceSpeed(name)
	if err == nil && speed > 0 {
		iface.Speed = &speed
	}
	// --- END SPEED COLLECTION ---
	
	return iface, nil
}

// parseLinkState converts the operstate string to LinkState
func (ic *InterfaceCollector) parseLinkState(operstate string) models.LinkState {
	switch strings.ToUpper(operstate) {
	case "UP":
		return models.LinkStateUP
	case "DOWN":
		return models.LinkStateDOWN
	default:
		return models.LinkStateUNKNOWN
	}
}

// determineInterfaceType determines the type of interface based on its name
func (ic *InterfaceCollector) determineInterfaceType(name string) models.InterfaceType {
	if name == "lo" {
		return models.InterfaceTypeLOOPBACK
	}
	
	// Check if it's a virtual interface
	iface := &models.NetworkInterface{Name: name}
	if iface.IsVirtualInterface() {
		return models.InterfaceTypeVIRTUAL
	}
	
	return models.InterfaceTypePHYSICAL
}

// detectIPConfigType detects whether an interface uses DHCP or static IP configuration
func (ic *InterfaceCollector) detectIPConfigType(interfaceName string) models.IPConfigType {
	// Check cache first
	if configType, exists := ic.ipConfigCache[interfaceName]; exists {
		return configType
	}
	
	// For virtual interfaces, return Unknown quickly
	iface := &models.NetworkInterface{Name: interfaceName}
	if iface.IsVirtualInterface() {
		ic.ipConfigCache[interfaceName] = models.IPConfigUnknown
		return models.IPConfigUnknown
	}
	
	// Try to detect DHCP vs Static configuration
	configType := ic.detectDHCPvsStatic(interfaceName)
	
	ic.ipConfigCache[interfaceName] = configType
	return configType
}

// detectDHCPvsStatic checks if an interface is configured for DHCP or static IP
func (ic *InterfaceCollector) detectDHCPvsStatic(interfaceName string) models.IPConfigType {
	// Method 1: Check systemd-networkd configuration
	if ic.checkSystemdNetworkd(interfaceName) {
		config := ic.getSystemdNetworkdConfig(interfaceName)
		if config != models.IPConfigUnknown {
			return config
		}
		// If systemd-networkd didn't find specific config, continue to other methods
	}
	
	// Method 2: Check NetworkManager configuration
	if ic.checkNetworkManager(interfaceName) {
		config := ic.getNetworkManagerConfig(interfaceName)
		if config != models.IPConfigUnknown {
			return config
		}
	}
	
	// Method 3: Check traditional /etc/network/interfaces
	if ic.checkTraditionalConfig(interfaceName) {
		config := ic.getTraditionalConfig(interfaceName)
		if config != models.IPConfigUnknown {
			return config
		}
	}
	
	// Method 4: Check routing table for DHCP indicators
	if ic.checkRoutingTableForDHCP(interfaceName) {
		return models.IPConfigDHCP
	}
	
	// Method 5: Check if interface has IP but no config files (likely DHCP)
	if ic.hasIPAddress(interfaceName) {
		return models.IPConfigDHCP
	}
	
	return models.IPConfigUnknown
}

// checkSystemdNetworkd checks if systemd-networkd is managing the interface
func (ic *InterfaceCollector) checkSystemdNetworkd(interfaceName string) bool {
	cmd := exec.Command("systemctl", "is-active", "systemd-networkd")
	output, err := cmd.Output()
	if err != nil {
		return false
	}
	return strings.TrimSpace(string(output)) == "active"
}

// getSystemdNetworkdConfig checks systemd-networkd configuration for DHCP vs static
func (ic *InterfaceCollector) getSystemdNetworkdConfig(interfaceName string) models.IPConfigType {
	// Check /etc/systemd/network/ for interface-specific config
	configPath := fmt.Sprintf("/etc/systemd/network/10-%s.network", interfaceName)
	if ic.fileExists(configPath) {
		content, err := ic.readFile(configPath)
		if err == nil {
			if strings.Contains(content, "[DHCP]") || strings.Contains(content, "DHCP=yes") {
				return models.IPConfigDHCP
			}
			if strings.Contains(content, "[Address]") || strings.Contains(content, "Address=") {
				return models.IPConfigStatic
			}
		}
	}
	
	// Check for wildcard configs
	wildcardConfigs := []string{
		"/etc/systemd/network/20-dhcp.network",
		"/etc/systemd/network/20-ethernet.network",
	}
	
	for _, config := range wildcardConfigs {
		if ic.fileExists(config) {
			content, err := ic.readFile(config)
			if err == nil {
				if strings.Contains(content, "[DHCP]") || strings.Contains(content, "DHCP=yes") {
					return models.IPConfigDHCP
				}
			}
		}
	}
	
	return models.IPConfigUnknown
}

// checkNetworkManager checks if NetworkManager is managing the interface
func (ic *InterfaceCollector) checkNetworkManager(interfaceName string) bool {
	cmd := exec.Command("systemctl", "is-active", "NetworkManager")
	output, err := cmd.Output()
	if err != nil {
		return false
	}
	return strings.TrimSpace(string(output)) == "active"
}

// getNetworkManagerConfig checks NetworkManager configuration for DHCP vs static
func (ic *InterfaceCollector) getNetworkManagerConfig(interfaceName string) models.IPConfigType {
	// Check NetworkManager connection files
	cmd := exec.Command("nmcli", "-t", "-f", "NAME,DEVICE", "connection", "show", "--active")
	output, err := cmd.Output()
	if err != nil {
		return models.IPConfigUnknown
	}
	
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		parts := strings.Split(line, ":")
		if len(parts) >= 2 && strings.TrimSpace(parts[1]) == interfaceName {
			connName := strings.TrimSpace(parts[0])
			return ic.getNMConnectionType(connName)
		}
	}
	
	return models.IPConfigUnknown
}

// getNMConnectionType gets the connection type from NetworkManager
func (ic *InterfaceCollector) getNMConnectionType(connectionName string) models.IPConfigType {
	cmd := exec.Command("nmcli", "-t", "-f", "IP4.ADDRESS", "connection", "show", connectionName)
	output, err := cmd.Output()
	if err != nil {
		return models.IPConfigUnknown
	}
	
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line != "" && line != "IP4.ADDRESS:" {
			// If we have a specific IP address, it's likely static
			if strings.Contains(line, "/") {
				return models.IPConfigStatic
			}
		}
	}
	
	// Check if DHCP is enabled
	cmd = exec.Command("nmcli", "-t", "-f", "IP4.DHCP", "connection", "show", connectionName)
	output, err = cmd.Output()
	if err == nil {
		if strings.Contains(string(output), "yes") {
			return models.IPConfigDHCP
		}
	}
	
	return models.IPConfigUnknown
}

// checkTraditionalConfig checks for traditional /etc/network/interfaces configuration
func (ic *InterfaceCollector) checkTraditionalConfig(interfaceName string) bool {
	return ic.fileExists("/etc/network/interfaces")
}

// getTraditionalConfig checks traditional network configuration for DHCP vs static
func (ic *InterfaceCollector) getTraditionalConfig(interfaceName string) models.IPConfigType {
	content, err := ic.readFile("/etc/network/interfaces")
	if err != nil {
		return models.IPConfigUnknown
	}
	
	lines := strings.Split(content, "\n")
	inInterface := false
	
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "iface "+interfaceName) {
			inInterface = true
			continue
		}
		
		if inInterface {
			if strings.HasPrefix(line, "iface ") {
				// New interface section, stop looking
				break
			}
			
			if strings.Contains(line, "dhcp") || strings.Contains(line, "dhclient") {
				return models.IPConfigDHCP
			}
			
			if strings.Contains(line, "address ") || strings.Contains(line, "netmask ") {
				return models.IPConfigStatic
			}
		}
	}
	
	return models.IPConfigUnknown
}

// hasIPAddress checks if the interface has an IP address (implies some kind of configuration)
func (ic *InterfaceCollector) hasIPAddress(interfaceName string) bool {
	cmd := exec.Command("ip", "-j", "addr", "show", interfaceName)
	output, err := cmd.Output()
	if err != nil {
		return false
	}
	
	var data []map[string]interface{}
	if err := json.Unmarshal(output, &data); err != nil {
		return false
	}
	
	for _, iface := range data {
		if addrInfo, ok := iface["addr_info"].([]interface{}); ok {
			if len(addrInfo) > 0 {
				return true
			}
		}
	}
	
	return false
}

// fileExists checks if a file exists
func (ic *InterfaceCollector) fileExists(path string) bool {
	cmd := exec.Command("test", "-f", path)
	return cmd.Run() == nil
}

// readFile reads a file and returns its content
func (ic *InterfaceCollector) readFile(path string) (string, error) {
	cmd := exec.Command("cat", path)
	output, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return string(output), nil
}

// checkRoutingTableForDHCP checks the routing table for DHCP indicators
func (ic *InterfaceCollector) checkRoutingTableForDHCP(interfaceName string) bool {
	cmd := exec.Command("ip", "route", "show")
	output, err := cmd.Output()
	if err != nil {
		return false
	}
	
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.Contains(line, "dev "+interfaceName) && strings.Contains(line, "proto dhcp") {
			return true
		}
	}
	
	return false
}

// RefreshInterfaces clears the cache and refreshes interface data
func (ic *InterfaceCollector) RefreshInterfaces() (*models.InterfaceCollection, error) {
	ic.ipConfigCache = make(map[string]models.IPConfigType)
	return ic.GetAllInterfaces()
}

// GetInterfaceDetails returns details for a specific interface
func (ic *InterfaceCollector) GetInterfaceDetails(interfaceName string) (*models.NetworkInterface, error) {
	interfaces, err := ic.GetAllInterfaces()
	if err != nil {
		return nil, err
	}
	
	iface := interfaces.GetInterface(interfaceName)
	if iface == nil {
		return nil, fmt.Errorf("interface '%s' not found", interfaceName)
	}
	
	return iface, nil
} 

// getInterfaceSpeed runs ethtool and parses the Speed line for a given interface
func getInterfaceSpeed(ifaceName string) (int, error) {
	cmd := exec.Command("ethtool", ifaceName)
	output, err := cmd.Output()
	if err != nil {
		return 0, err
	}
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "Speed:") {
			// Example: Speed: 1000Mb/s
			parts := strings.Fields(line)
			if len(parts) >= 2 && strings.HasSuffix(parts[1], "Mb/s") {
				speedStr := strings.TrimSuffix(parts[1], "Mb/s")
				speedStr = strings.TrimSpace(speedStr)
				speedVal, err := strconv.Atoi(speedStr)
				if err == nil {
					return speedVal, nil
				}
			}
		}
	}
	return 0, fmt.Errorf("speed not found")
} 