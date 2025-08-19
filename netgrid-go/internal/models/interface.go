package models

import (
	"fmt"
	"net"
	"strings"
)

// LinkState represents the operational state of a network interface
type LinkState string

const (
	LinkStateUP      LinkState = "UP"
	LinkStateDOWN    LinkState = "DOWN"
	LinkStateUNKNOWN LinkState = "UNKNOWN"
)

// InterfaceType represents the type of network interface
type InterfaceType string

const (
	InterfaceTypePHYSICAL InterfaceType = "PHYSICAL"
	InterfaceTypeVIRTUAL  InterfaceType = "VIRTUAL"
	InterfaceTypeLOOPBACK InterfaceType = "LOOPBACK"
)

// DuplexMode represents the duplex mode of an interface
type DuplexMode string

const (
	DuplexModeFULL    DuplexMode = "FULL"
	DuplexModeHALF    DuplexMode = "HALF"
	DuplexModeUNKNOWN DuplexMode = "UNKNOWN"
)

// IPConfigType represents the IP configuration type
type IPConfigType string

const (
	IPConfigDHCP   IPConfigType = "DHCP"
	IPConfigStatic IPConfigType = "Static"
	IPConfigUnknown IPConfigType = "Unknown"
)

// NetworkInterface represents a network interface with all its properties
type NetworkInterface struct {
	Name          string
	LinkState     LinkState
	Speed         *int // Speed in Mbps, nil if unknown
	MACAddress    string
	IPAddresses   []string
	MTU           *int
	Driver        string
	InterfaceType InterfaceType
	Vendor        string
	IPConfigType  IPConfigType
	Description   string
	Flags         []string
	Duplex        DuplexMode
	ExtraData     map[string]interface{}
}

// IsUp returns true if the interface is in UP state
func (ni *NetworkInterface) IsUp() bool {
	return ni.LinkState == LinkStateUP
}

// PrimaryIP returns the first IPv4 address, or empty string if none
func (ni *NetworkInterface) PrimaryIP() string {
	for _, ip := range ni.IPAddresses {
		if !strings.Contains(ip, ":") { // IPv4 check
			return ip
		}
	}
	return ""
}

// NormalizeMACAddress normalizes a MAC address to standard format
func (ni *NetworkInterface) NormalizeMACAddress() {
	if ni.MACAddress == "" {
		return
	}
	
	// Remove common separators
	mac := strings.ReplaceAll(ni.MACAddress, ":", "")
	mac = strings.ReplaceAll(mac, "-", "")
	mac = strings.ReplaceAll(mac, ".", "")
	
	// Convert to uppercase
	mac = strings.ToUpper(mac)
	
	// Validate MAC address format (6 bytes = 12 hex characters)
	if len(mac) != 12 {
		ni.MACAddress = ""
		return
	}
	
	// Add colons every 2 characters
	var parts []string
	for i := 0; i < 12; i += 2 {
		parts = append(parts, mac[i:i+2])
	}
	ni.MACAddress = strings.Join(parts, ":")
}

// Validate validates the network interface data
func (ni *NetworkInterface) Validate() error {
	if ni.Name == "" {
		return fmt.Errorf("interface name cannot be empty")
	}
	
	if ni.MACAddress != "" {
		// Validate MAC address format
		_, err := net.ParseMAC(ni.MACAddress)
		if err != nil {
			return fmt.Errorf("invalid MAC address format: %s", ni.MACAddress)
		}
	}
	
	// Validate IP addresses
	for _, ip := range ni.IPAddresses {
		if net.ParseIP(ip) == nil {
			return fmt.Errorf("invalid IP address: %s", ip)
		}
	}
	
	return nil
}

// String returns a string representation of the interface
func (ni *NetworkInterface) String() string {
	return fmt.Sprintf("Interface{Name: %s, State: %s, Type: %s}", 
		ni.Name, ni.LinkState, ni.InterfaceType)
}

// ToMap converts the interface to a map for serialization
func (ni *NetworkInterface) ToMap() map[string]interface{} {
	result := map[string]interface{}{
		"name":           ni.Name,
		"link_state":     string(ni.LinkState),
		"mac_address":    ni.MACAddress,
		"ip_addresses":   ni.IPAddresses,
		"interface_type": string(ni.InterfaceType),
		"vendor":         ni.Vendor,
		"ip_config_type": string(ni.IPConfigType),
		"description":    ni.Description,
		"flags":          ni.Flags,
		"duplex":         string(ni.Duplex),
		"extra_data":     ni.ExtraData,
	}
	
	if ni.Speed != nil {
		result["speed"] = *ni.Speed
	}
	if ni.MTU != nil {
		result["mtu"] = *ni.MTU
	}
	if ni.Driver != "" {
		result["driver"] = ni.Driver
	}
	
	return result
}

// IsVirtualInterface checks if the interface is virtual
func (ni *NetworkInterface) IsVirtualInterface() bool {
	virtualPrefixes := []string{"veth", "br-", "docker", "virbr"}
	virtualNames := []string{"lo", "vmsgohere"}
	
	// Check prefixes
	for _, prefix := range virtualPrefixes {
		if strings.HasPrefix(ni.Name, prefix) {
			return true
		}
	}
	
	// Check exact names
	for _, name := range virtualNames {
		if ni.Name == name {
			return true
		}
	}
	
	// Check tailscale prefix
	if strings.HasPrefix(ni.Name, "tailscale") {
		return true
	}
	
	return false
}

// InterfaceCollection represents a collection of network interfaces
type InterfaceCollection struct {
	Interfaces []*NetworkInterface
}

// NewInterfaceCollection creates a new empty interface collection
func NewInterfaceCollection() *InterfaceCollection {
	return &InterfaceCollection{
		Interfaces: make([]*NetworkInterface, 0),
	}
}

// AddInterface adds an interface to the collection
func (ic *InterfaceCollection) AddInterface(iface *NetworkInterface) {
	if iface != nil {
		ic.Interfaces = append(ic.Interfaces, iface)
	}
}

// GetInterface returns an interface by name, or nil if not found
func (ic *InterfaceCollection) GetInterface(name string) *NetworkInterface {
	for _, iface := range ic.Interfaces {
		if iface.Name == name {
			return iface
		}
	}
	return nil
}

// FilterByState returns interfaces filtered by link state
func (ic *InterfaceCollection) FilterByState(state LinkState) []*NetworkInterface {
	var result []*NetworkInterface
	for _, iface := range ic.Interfaces {
		if iface.LinkState == state {
			result = append(result, iface)
		}
	}
	return result
}

// FilterByType returns interfaces filtered by interface type
func (ic *InterfaceCollection) FilterByType(ifaceType InterfaceType) []*NetworkInterface {
	var result []*NetworkInterface
	for _, iface := range ic.Interfaces {
		if iface.InterfaceType == ifaceType {
			result = append(result, iface)
		}
	}
	return result
}

// FilterUpAndDown returns interfaces that are either UP or DOWN
func (ic *InterfaceCollection) FilterUpAndDown() []*NetworkInterface {
	var result []*NetworkInterface
	for _, iface := range ic.Interfaces {
		if iface.LinkState == LinkStateUP || iface.LinkState == LinkStateDOWN {
			result = append(result, iface)
		}
	}
	return result
}

// SortByName sorts interfaces by name
func (ic *InterfaceCollection) SortByName() {
	// TODO: Implement sorting logic
}

// ToMap converts the collection to a map for serialization
func (ic *InterfaceCollection) ToMap() map[string]interface{} {
	interfaces := make([]map[string]interface{}, len(ic.Interfaces))
	for i, iface := range ic.Interfaces {
		interfaces[i] = iface.ToMap()
	}
	
	return map[string]interface{}{
		"interfaces": interfaces,
		"count":      len(ic.Interfaces),
	}
} 