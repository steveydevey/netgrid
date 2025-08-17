package collector

import (
	"fmt"
	"net"
	"os"
	"os/exec"
	"regexp"
	"runtime"
	"strconv"
	"strings"

	"netgrid/internal/models"
)

// InterfaceCollector collects network interface information from the system
type InterfaceCollector struct {
	enableVendorLookup bool
}

// NewInterfaceCollector creates a new interface collector
func NewInterfaceCollector(enableVendorLookup bool) *InterfaceCollector {
	return &InterfaceCollector{
		enableVendorLookup: enableVendorLookup,
	}
}

// GetAllInterfaces retrieves all network interfaces from the system
func (ic *InterfaceCollector) GetAllInterfaces() ([]models.NetworkInterface, error) {
	interfaces, err := net.Interfaces()
	if err != nil {
		return nil, fmt.Errorf("failed to get network interfaces: %w", err)
	}

	var result []models.NetworkInterface

	for _, iface := range interfaces {
		netInterface, err := ic.collectInterfaceInfo(iface)
		if err != nil {
			// Log error but continue with other interfaces
			continue
		}
		result = append(result, netInterface)
	}

	return result, nil
}

// collectInterfaceInfo collects detailed information about a single interface
func (ic *InterfaceCollector) collectInterfaceInfo(iface net.Interface) (models.NetworkInterface, error) {
	netIface := models.NetworkInterface{
		Name:         iface.Name,
		MACAddress:   iface.HardwareAddr.String(),
		IPAddresses:  []string{},
		LinkState:    models.LinkStateUnknown,
		IPConfigType: "Unknown",
		Flags:        []string{},
	}

	// Classify interface type
	netIface.ClassifyInterfaceType()

	// Determine link state from flags
	if iface.Flags&net.FlagUp != 0 {
		netIface.LinkState = models.LinkStateUp
	} else {
		netIface.LinkState = models.LinkStateDown
	}

	// Extract flag information
	netIface.Flags = ic.extractFlags(iface.Flags)

	// Get IP addresses
	addrs, err := iface.Addrs()
	if err == nil {
		for _, addr := range addrs {
			if ipNet, ok := addr.(*net.IPNet); ok {
				netIface.IPAddresses = append(netIface.IPAddresses, ipNet.IP.String())
			}
		}
	}

	// Get MTU
	mtu := iface.MTU
	netIface.MTU = &mtu

	// Get additional information from /sys (Linux-specific)
	ic.enrichFromSysfs(&netIface)

	// Get vendor information if enabled
	if ic.enableVendorLookup && netIface.MACAddress != "" {
		vendor := ic.lookupVendor(netIface.MACAddress)
		netIface.Vendor = vendor
	}

	return netIface, nil
}

// extractFlags converts net.Flags to string slice
func (ic *InterfaceCollector) extractFlags(flags net.Flags) []string {
	var flagList []string

	if flags&net.FlagUp != 0 {
		flagList = append(flagList, "UP")
	}
	if flags&net.FlagBroadcast != 0 {
		flagList = append(flagList, "BROADCAST")
	}
	if flags&net.FlagLoopback != 0 {
		flagList = append(flagList, "LOOPBACK")
	}
	if flags&net.FlagPointToPoint != 0 {
		flagList = append(flagList, "POINTOPOINT")
	}
	if flags&net.FlagMulticast != 0 {
		flagList = append(flagList, "MULTICAST")
	}

	return flagList
}

// enrichFromSysfs adds additional information from system-specific sources
func (ic *InterfaceCollector) enrichFromSysfs(iface *models.NetworkInterface) {
	switch runtime.GOOS {
	case "linux":
		ic.enrichLinux(iface)
	case "darwin":
		ic.enrichMacOS(iface)
	default:
		// For other operating systems, try to determine IP config at least
		ic.determineIPConfigType(iface)
	}
}

// enrichLinux adds Linux-specific information from /sys filesystem
func (ic *InterfaceCollector) enrichLinux(iface *models.NetworkInterface) {
	// Speed information
	speedPath := fmt.Sprintf("/sys/class/net/%s/speed", iface.Name)
	if speed := ic.readIntFromFile(speedPath); speed > 0 {
		iface.Speed = &speed
	}

	// Driver information
	driverPath := fmt.Sprintf("/sys/class/net/%s/device/driver", iface.Name)
	if driver := ic.readSymlinkBasename(driverPath); driver != "" {
		iface.Driver = driver
	}

	// Duplex information
	duplexPath := fmt.Sprintf("/sys/class/net/%s/duplex", iface.Name)
	if duplex := ic.readStringFromFile(duplexPath); duplex != "" {
		switch strings.ToLower(strings.TrimSpace(duplex)) {
		case "full":
			iface.Duplex = models.DuplexFull
		case "half":
			iface.Duplex = models.DuplexHalf
		}
	}

	// Try to determine IP configuration type
	ic.determineIPConfigType(iface)
}

// enrichMacOS adds macOS-specific information using system commands
func (ic *InterfaceCollector) enrichMacOS(iface *models.NetworkInterface) {
	// Get speed information using networksetup
	if speed := ic.getMacOSInterfaceSpeed(iface.Name); speed > 0 {
		iface.Speed = &speed
	}

	// Get driver information using system_profiler (for Ethernet interfaces)
	if driver := ic.getMacOSDriver(iface.Name); driver != "" {
		iface.Driver = driver
	}

	// Try to determine IP configuration type
	ic.determineMacOSIPConfigType(iface)
}

// readIntFromFile reads an integer value from a file
func (ic *InterfaceCollector) readIntFromFile(path string) int {
	content, err := os.ReadFile(path)
	if err != nil {
		return 0
	}

	value, err := strconv.Atoi(strings.TrimSpace(string(content)))
	if err != nil {
		return 0
	}

	return value
}

// readStringFromFile reads a string value from a file
func (ic *InterfaceCollector) readStringFromFile(path string) string {
	content, err := os.ReadFile(path)
	if err != nil {
		return ""
	}

	return strings.TrimSpace(string(content))
}

// readSymlinkBasename reads a symlink and returns the basename
func (ic *InterfaceCollector) readSymlinkBasename(path string) string {
	target, err := os.Readlink(path)
	if err != nil {
		return ""
	}

	parts := strings.Split(target, "/")
	if len(parts) > 0 {
		return parts[len(parts)-1]
	}

	return ""
}

// determineIPConfigType tries to determine if interface uses DHCP or static IP
func (ic *InterfaceCollector) determineIPConfigType(iface *models.NetworkInterface) {
	if len(iface.IPAddresses) == 0 {
		iface.IPConfigType = "None"
		return
	}

	// Check for DHCP lease files (common locations)
	dhcpPaths := []string{
		fmt.Sprintf("/var/lib/dhcp/dhclient.%s.leases", iface.Name),
		fmt.Sprintf("/var/lib/dhclient/dhclient-%s.leases", iface.Name),
		fmt.Sprintf("/var/lib/NetworkManager/dhclient-%s.lease", iface.Name),
	}

	for _, path := range dhcpPaths {
		if _, err := os.Stat(path); err == nil {
			iface.IPConfigType = "DHCP"
			return
		}
	}

	// Check systemd-networkd DHCP
	networkdPath := fmt.Sprintf("/run/systemd/netif/leases/%s", iface.Name)
	if _, err := os.Stat(networkdPath); err == nil {
		iface.IPConfigType = "DHCP"
		return
	}

	// If we can't determine, assume static for interfaces with IPs
	iface.IPConfigType = "Static"
}

// lookupVendor performs vendor lookup for MAC address (placeholder implementation)
func (ic *InterfaceCollector) lookupVendor(macAddress string) string {
	// This is a simplified vendor lookup
	// In a real implementation, you would query OUI databases
	
	if macAddress == "" {
		return ""
	}

	// Extract OUI (first 3 octets)
	parts := strings.Split(macAddress, ":")
	if len(parts) < 3 {
		return ""
	}

	oui := strings.ToUpper(strings.Join(parts[:3], ":"))

	// Simple vendor mapping (you would typically use a proper OUI database)
	vendors := map[string]string{
		"00:0C:29": "VMware",
		"00:15:5D": "Microsoft",
		"00:16:3E": "Xen",
		"00:1C:42": "Parallels",
		"00:50:56": "VMware",
		"08:00:27": "VirtualBox",
		"52:54:00": "QEMU",
		"00:E0:4C": "Realtek",
		"00:1B:21": "Intel",
		"00:14:22": "Intel",
		"00:15:17": "Intel",
		"00:19:D1": "Intel",
		"00:1E:67": "Intel",
		"00:24:81": "Intel",
		"A0:36:9F": "Intel",
		"C4:34:6B": "Hewlett Packard",
		"HP": "Hewlett Packard Enterprise",
	}

	if vendor, exists := vendors[oui]; exists {
		return vendor
	}

	return ""
}

// FilterNonVirtual filters out virtual interfaces
func FilterNonVirtual(interfaces []models.NetworkInterface) []models.NetworkInterface {
	var filtered []models.NetworkInterface
	for _, iface := range interfaces {
		if !iface.IsVirtual() {
			filtered = append(filtered, iface)
		}
	}
	return filtered
}

// getMacOSInterfaceSpeed gets speed information for macOS interfaces
func (ic *InterfaceCollector) getMacOSInterfaceSpeed(interfaceName string) int {
	// For Wi-Fi interfaces, try AirPort data first
	if strings.HasPrefix(interfaceName, "en") {
		if speed := ic.getWiFiSpeed(interfaceName); speed > 0 {
			return speed
		}
	}
	
	// Try networksetup command first
	cmd := exec.Command("networksetup", "-getnetworkserviceenabled", interfaceName)
	if err := cmd.Run(); err == nil {
		// Interface is managed by networksetup, try to get speed
		speedCmd := exec.Command("networksetup", "-getMedia", interfaceName)
		output, err := speedCmd.Output()
		if err == nil {
			return ic.parseNetworksetupSpeed(string(output))
		}
	}
	
	// Try system_profiler for hardware info
	cmd = exec.Command("system_profiler", "SPNetworkDataType", "-xml")
	output, err := cmd.Output()
	if err == nil {
		return ic.parseSystemProfilerSpeed(string(output), interfaceName)
	}
	
	// Try ifconfig for basic link info
	cmd = exec.Command("ifconfig", interfaceName)
	output, err = cmd.Output()
	if err == nil {
		return ic.parseIfconfigSpeed(string(output))
	}
	
	return 0
}

// parseNetworksetupSpeed parses speed from networksetup output
func (ic *InterfaceCollector) parseNetworksetupSpeed(output string) int {
	// Look for speed patterns like "1000baseT", "100baseT", etc.
	speedRegex := regexp.MustCompile(`(\d+)base`)
	matches := speedRegex.FindStringSubmatch(output)
	if len(matches) > 1 {
		if speed, err := strconv.Atoi(matches[1]); err == nil {
			return speed
		}
	}
	return 0
}

// parseSystemProfilerSpeed parses speed from system_profiler output
func (ic *InterfaceCollector) parseSystemProfilerSpeed(output, interfaceName string) int {
	// This is a simplified parser - system_profiler XML is complex
	// Look for speed values in the XML
	speedRegex := regexp.MustCompile(`<key>speed</key>\s*<string>(\d+)\s*Mb`)
	matches := speedRegex.FindStringSubmatch(output)
	if len(matches) > 1 {
		if speed, err := strconv.Atoi(matches[1]); err == nil {
			return speed
		}
	}
	return 0
}

// parseIfconfigSpeed parses speed from ifconfig output
func (ic *InterfaceCollector) parseIfconfigSpeed(output string) int {
	// Look for media information in ifconfig output
	// Example: "media: autoselect (1000baseT <full-duplex>)"
	mediaRegex := regexp.MustCompile(`media:.*\((\d+)base`)
	matches := mediaRegex.FindStringSubmatch(output)
	if len(matches) > 1 {
		if speed, err := strconv.Atoi(matches[1]); err == nil {
			return speed
		}
	}
	return 0
}

// getMacOSDriver gets driver information for macOS interfaces
func (ic *InterfaceCollector) getMacOSDriver(interfaceName string) string {
	// Use system_profiler to get hardware information
	cmd := exec.Command("system_profiler", "SPNetworkDataType")
	output, err := cmd.Output()
	if err != nil {
		return ""
	}
	
	// Parse the output to find driver information
	return ic.parseDriverFromSystemProfiler(string(output), interfaceName)
}

// parseDriverFromSystemProfiler parses driver info from system_profiler output
func (ic *InterfaceCollector) parseDriverFromSystemProfiler(output, interfaceName string) string {
	// This is a simplified implementation
	// Look for common driver patterns
	lines := strings.Split(output, "\n")
	for _, line := range lines {
		if strings.Contains(line, interfaceName) {
			// Check following lines for driver info
			// This would need more sophisticated parsing in practice
			if strings.Contains(line, "Ethernet") {
				return "ethernet"
			}
		}
	}
	return ""
}

// determineMacOSIPConfigType determines IP configuration type on macOS
func (ic *InterfaceCollector) determineMacOSIPConfigType(iface *models.NetworkInterface) {
	if len(iface.IPAddresses) == 0 {
		iface.IPConfigType = "None"
		return
	}
	
	// Check networksetup for DHCP configuration
	cmd := exec.Command("networksetup", "-getinfo", iface.Name)
	output, err := cmd.Output()
	if err == nil {
		outputStr := string(output)
		if strings.Contains(outputStr, "DHCP Configuration") {
			iface.IPConfigType = "DHCP"
			return
		}
		if strings.Contains(outputStr, "Manual Configuration") {
			iface.IPConfigType = "Static"
			return
		}
	}
	
	// Fallback: assume static if we have IPs but can't determine type
	iface.IPConfigType = "Static"
}

// getWiFiSpeed gets the current Wi-Fi connection speed from AirPort data
func (ic *InterfaceCollector) getWiFiSpeed(interfaceName string) int {
	// Use system_profiler to get AirPort specific data
	cmd := exec.Command("system_profiler", "SPAirPortDataType")
	output, err := cmd.Output()
	if err != nil {
		return 0
	}
	
	return ic.parseAirPortSpeed(string(output), interfaceName)
}

// parseAirPortSpeed parses Wi-Fi speed from SPAirPortDataType output
func (ic *InterfaceCollector) parseAirPortSpeed(output, interfaceName string) int {
	lines := strings.Split(output, "\n")
	inTargetInterface := false
	inCurrentNetwork := false
	
	for _, line := range lines {
		originalLine := line
		line = strings.TrimSpace(line)
		
		// Look for the interface section (e.g., "en0:")
		if strings.HasSuffix(line, interfaceName+":") {
			inTargetInterface = true
			continue
		}
		
		// Reset if we hit another interface at the same level
		if inTargetInterface && strings.HasSuffix(line, ":") && !strings.Contains(line, "Current Network") && !strings.Contains(line, "Transmit Rate") && !strings.HasPrefix(originalLine, "        ") {
			if !strings.Contains(line, interfaceName) {
				inTargetInterface = false
				inCurrentNetwork = false
			}
		}
		
		// Look for Current Network Information section
		if inTargetInterface && strings.Contains(line, "Current Network Information:") {
			inCurrentNetwork = true
			continue
		}
		
		// Look for Transmit Rate within current network
		if inTargetInterface && inCurrentNetwork && strings.Contains(line, "Transmit Rate:") {
			// Extract speed value
			parts := strings.Split(line, ":")
			if len(parts) > 1 {
				speedStr := strings.TrimSpace(parts[1])
				if speed, err := strconv.Atoi(speedStr); err == nil {
					return speed
				}
			}
		}
		
		// Reset current network if we're back to interface level
		if inTargetInterface && inCurrentNetwork && !strings.HasPrefix(originalLine, "          ") && strings.Contains(line, ":") && !strings.Contains(line, "Transmit Rate") {
			inCurrentNetwork = false
		}
	}
	
	return 0
}