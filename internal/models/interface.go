package models

import (
	"fmt"
	"net"
	"strings"
)

// LinkState represents the state of a network interface
type LinkState int

const (
	LinkStateUnknown LinkState = iota
	LinkStateUp
	LinkStateDown
)

func (ls LinkState) String() string {
	switch ls {
	case LinkStateUp:
		return "up"
	case LinkStateDown:
		return "down"
	default:
		return "unknown"
	}
}

// InterfaceType represents the type of network interface
type InterfaceType int

const (
	InterfaceTypeUnknown InterfaceType = iota
	InterfaceTypePhysical
	InterfaceTypeVirtual
	InterfaceTypeLoopback
	InterfaceTypeWireless
	InterfaceTypeBridge
)

func (it InterfaceType) String() string {
	switch it {
	case InterfaceTypePhysical:
		return "physical"
	case InterfaceTypeVirtual:
		return "virtual"
	case InterfaceTypeLoopback:
		return "loopback"
	case InterfaceTypeWireless:
		return "wireless"
	case InterfaceTypeBridge:
		return "bridge"
	default:
		return "unknown"
	}
}

// DuplexMode represents the duplex mode of an interface
type DuplexMode int

const (
	DuplexUnknown DuplexMode = iota
	DuplexFull
	DuplexHalf
)

func (dm DuplexMode) String() string {
	switch dm {
	case DuplexFull:
		return "full"
	case DuplexHalf:
		return "half"
	default:
		return "unknown"
	}
}

// NetworkInterface represents a network interface with all its properties
type NetworkInterface struct {
	// Basic properties
	Name       string   `json:"name"`
	MACAddress string   `json:"mac_address,omitempty"`
	IPAddresses []string `json:"ip_addresses"`

	// Status information
	LinkState LinkState   `json:"link_state"`
	Speed     *int        `json:"speed,omitempty"` // Speed in Mbps
	Duplex    DuplexMode  `json:"duplex"`

	// Configuration
	MTU           *int          `json:"mtu,omitempty"`
	Driver        string        `json:"driver,omitempty"`
	InterfaceType InterfaceType `json:"interface_type"`

	// Vendor information
	Vendor string `json:"vendor,omitempty"`

	// IP configuration type
	IPConfigType string `json:"ip_config_type"`

	// Additional metadata
	Description string            `json:"description,omitempty"`
	Flags       []string          `json:"flags"`
	ExtraData   map[string]interface{} `json:"extra_data,omitempty"`
}

// IsUp returns true if the interface is up
func (ni *NetworkInterface) IsUp() bool {
	return ni.LinkState == LinkStateUp
}

// IsPhysical returns true if this is a physical interface
func (ni *NetworkInterface) IsPhysical() bool {
	return ni.InterfaceType == InterfaceTypePhysical
}

// HasIP returns true if the interface has any IP addresses
func (ni *NetworkInterface) HasIP() bool {
	return len(ni.IPAddresses) > 0
}

// PrimaryIP returns the primary IP address (first IPv4, then first IPv6)
func (ni *NetworkInterface) PrimaryIP() string {
	if len(ni.IPAddresses) == 0 {
		return ""
	}

	// Prefer IPv4 addresses
	for _, ip := range ni.IPAddresses {
		if net.ParseIP(ip).To4() != nil {
			return ip
		}
	}

	// Fall back to IPv6
	return ni.IPAddresses[0]
}

// GetIPv4Addresses returns only IPv4 addresses
func (ni *NetworkInterface) GetIPv4Addresses() []string {
	var ipv4s []string
	for _, ip := range ni.IPAddresses {
		if net.ParseIP(ip).To4() != nil {
			ipv4s = append(ipv4s, ip)
		}
	}
	return ipv4s
}

// GetIPv6Addresses returns only IPv6 addresses
func (ni *NetworkInterface) GetIPv6Addresses() []string {
	var ipv6s []string
	for _, ip := range ni.IPAddresses {
		if net.ParseIP(ip).To4() == nil && net.ParseIP(ip) != nil {
			ipv6s = append(ipv6s, ip)
		}
	}
	return ipv6s
}

// FormatSpeed formats the speed value for display
func (ni *NetworkInterface) FormatSpeed() string {
	if ni.Speed == nil {
		return "-"
	}

	speed := *ni.Speed
	if speed >= 1000 {
		return fmt.Sprintf("%.0fGbps", float64(speed)/1000)
	}
	return fmt.Sprintf("%dMbps", speed)
}

// String returns a string representation of the interface
func (ni *NetworkInterface) String() string {
	status := "DOWN"
	if ni.IsUp() {
		status = "UP"
	}

	ipInfo := ""
	if primaryIP := ni.PrimaryIP(); primaryIP != "" {
		ipInfo = fmt.Sprintf(" (%s)", primaryIP)
	}

	return fmt.Sprintf("%s: %s%s", ni.Name, status, ipInfo)
}

// IsVirtual returns true if the interface appears to be virtual
func (ni *NetworkInterface) IsVirtual() bool {
	name := strings.ToLower(ni.Name)
	virtualPrefixes := []string{"veth", "br-", "tailscale", "vmsgohere"}
	
	for _, prefix := range virtualPrefixes {
		if strings.HasPrefix(name, prefix) {
			return true
		}
	}
	
	return name == "lo"
}

// ClassifyInterfaceType attempts to classify the interface type based on its name
func (ni *NetworkInterface) ClassifyInterfaceType() {
	name := strings.ToLower(ni.Name)
	
	switch {
	case name == "lo":
		ni.InterfaceType = InterfaceTypeLoopback
	case strings.HasPrefix(name, "veth") || strings.HasPrefix(name, "br-") || strings.HasPrefix(name, "tailscale"):
		ni.InterfaceType = InterfaceTypeVirtual
	case strings.HasPrefix(name, "wlan") || strings.HasPrefix(name, "wifi"):
		ni.InterfaceType = InterfaceTypeWireless
	case strings.HasPrefix(name, "eno") || strings.HasPrefix(name, "ens") || strings.HasPrefix(name, "eth"):
		ni.InterfaceType = InterfaceTypePhysical
	default:
		ni.InterfaceType = InterfaceTypeUnknown
	}
}

// InterfaceCollection represents a collection of network interfaces
type InterfaceCollection struct {
	Interfaces []NetworkInterface `json:"interfaces"`
}

// Add adds an interface to the collection
func (ic *InterfaceCollection) Add(iface NetworkInterface) {
	ic.Interfaces = append(ic.Interfaces, iface)
}

// FilterByState filters interfaces by link state
func (ic *InterfaceCollection) FilterByState(state LinkState) *InterfaceCollection {
	var filtered []NetworkInterface
	for _, iface := range ic.Interfaces {
		if iface.LinkState == state {
			filtered = append(filtered, iface)
		}
	}
	return &InterfaceCollection{Interfaces: filtered}
}

// FilterUp returns only interfaces that are up
func (ic *InterfaceCollection) FilterUp() *InterfaceCollection {
	return ic.FilterByState(LinkStateUp)
}

// FilterDown returns only interfaces that are down
func (ic *InterfaceCollection) FilterDown() *InterfaceCollection {
	return ic.FilterByState(LinkStateDown)
}

// FilterPhysical returns only physical interfaces
func (ic *InterfaceCollection) FilterPhysical() *InterfaceCollection {
	var filtered []NetworkInterface
	for _, iface := range ic.Interfaces {
		if iface.IsPhysical() {
			filtered = append(filtered, iface)
		}
	}
	return &InterfaceCollection{Interfaces: filtered}
}

// FilterNonVirtual returns interfaces that are not virtual
func (ic *InterfaceCollection) FilterNonVirtual() *InterfaceCollection {
	var filtered []NetworkInterface
	for _, iface := range ic.Interfaces {
		if !iface.IsVirtual() {
			filtered = append(filtered, iface)
		}
	}
	return &InterfaceCollection{Interfaces: filtered}
}

// Len returns the number of interfaces
func (ic *InterfaceCollection) Len() int {
	return len(ic.Interfaces)
}