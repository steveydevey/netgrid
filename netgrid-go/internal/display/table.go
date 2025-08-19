package display

import (
	"fmt"
	"os"
	"sort"
	"strings"

	"github.com/olekukonko/tablewriter"
	"github.com/netgrid/netgrid-go/internal/models"
)

// TableFormatter formats network interface data into beautiful tables
type TableFormatter struct {
	showVendors bool
	showIPv6    bool
	sortBy      string
}

// NewTableFormatter creates a new table formatter
func NewTableFormatter(showVendors, showIPv6 bool, sortBy string) *TableFormatter {
	return &TableFormatter{
		showVendors: showVendors,
		showIPv6:    showIPv6,
		sortBy:      sortBy,
	}
}

// FormatInterfacesTable formats a collection of interfaces into a table
func (tf *TableFormatter) FormatInterfacesTable(collection *models.InterfaceCollection) {
	// Sort interfaces
	interfaces := tf.sortInterfaces(collection.Interfaces)

	// Build header
	header := []string{"State/Name", "Speed", "MAC", "MTU", "IP Config"}
	if tf.showVendors {
		header = append(header, "Vendor")
	}
	header = append(header, "IP Addresses")

	table := tablewriter.NewWriter(os.Stdout)
	table.SetHeader(header)
	table.SetBorder(false)
	table.SetCenterSeparator("")
	table.SetColumnSeparator("")
	table.SetRowSeparator("")
	table.SetAlignment(tablewriter.ALIGN_LEFT)
	table.SetHeaderAlignment(tablewriter.ALIGN_LEFT)

	// Add rows
	for _, iface := range interfaces {
		row := tf.formatInterfaceRowCustom(iface)
		table.Append(row)
	}

	// Render table
	table.Render()
}

// sortInterfaces sorts interfaces by the specified criteria
func (tf *TableFormatter) sortInterfaces(interfaces []*models.NetworkInterface) []*models.NetworkInterface {
	sorted := make([]*models.NetworkInterface, len(interfaces))
	copy(sorted, interfaces)

	sort.Slice(sorted, func(i, j int) bool {
		switch tf.sortBy {
		case "name":
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		case "state":
			if sorted[i].IsUp() != sorted[j].IsUp() {
				return sorted[i].IsUp() // UP interfaces first
			}
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		case "speed":
			speedI := 0
			speedJ := 0
			if sorted[i].Speed != nil {
				speedI = *sorted[i].Speed
			}
			if sorted[j].Speed != nil {
				speedJ = *sorted[j].Speed
			}
			if speedI != speedJ {
				return speedI > speedJ // Higher speeds first
			}
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		case "mac":
			return sorted[i].MACAddress < sorted[j].MACAddress
		case "vendor":
			if sorted[i].Vendor != sorted[j].Vendor {
				return sorted[i].Vendor < sorted[j].Vendor
			}
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		case "ip":
			ipI := sorted[i].PrimaryIP()
			ipJ := sorted[j].PrimaryIP()
			if ipI != ipJ {
				return ipI < ipJ
			}
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		default:
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		}
	})

	return sorted
}

// formatInterfaceRowCustom formats a single interface into a table row, conditionally including columns
func (tf *TableFormatter) formatInterfaceRowCustom(iface *models.NetworkInterface) []string {
	// State/Name
	state := "x"
	if iface.IsUp() {
		state = "!"
	}
	name := fmt.Sprintf("%s %s", state, iface.Name)

	// Speed
	speed := tf.formatSpeed(iface)

	// MAC address
	mac := tf.formatMACAddress(iface)

	// MTU
	mtu := tf.formatMTU(iface)

	row := []string{name, speed, mac, mtu, tf.formatIPConfig(iface)}

	// Vendor
	if tf.showVendors {
		row = append(row, tf.formatVendor(iface))
	}

	// IP addresses
	row = append(row, tf.formatIPAddresses(iface))

	return row
}

// formatInterfaceName formats the interface name with color based on state
func (tf *TableFormatter) formatInterfaceName(iface *models.NetworkInterface) string {
	stateSymbol := "●"
	if iface.IsUp() {
		return fmt.Sprintf("%s %s", stateSymbol, iface.Name)
	} else {
		return fmt.Sprintf("%s %s", stateSymbol, iface.Name)
	}
}

// formatSpeed formats the speed field
func (tf *TableFormatter) formatSpeed(iface *models.NetworkInterface) string {
	if iface.Speed != nil {
		return fmt.Sprintf("%d", *iface.Speed)
	}
	return "-"
}

// formatMACAddress formats the MAC address field
func (tf *TableFormatter) formatMACAddress(iface *models.NetworkInterface) string {
	if iface.MACAddress != "" {
		return iface.MACAddress
	}
	return "-"
}

// formatMTU formats the MTU field
func (tf *TableFormatter) formatMTU(iface *models.NetworkInterface) string {
	if iface.MTU != nil {
		return fmt.Sprintf("%d", *iface.MTU)
	}
	return "-"
}

// formatIPConfig formats the IP configuration type
func (tf *TableFormatter) formatIPConfig(iface *models.NetworkInterface) string {
	return string(iface.IPConfigType)
}

// formatVendor formats the vendor field
func (tf *TableFormatter) formatVendor(iface *models.NetworkInterface) string {
	if !tf.showVendors {
		return ""
	}

	if iface.Vendor != "" {
		return iface.Vendor
	}
	return "-"
}

// formatIPAddresses formats the IP addresses field
func (tf *TableFormatter) formatIPAddresses(iface *models.NetworkInterface) string {
	if len(iface.IPAddresses) == 0 {
		return "-"
	}

	var addresses []string
	for _, ip := range iface.IPAddresses {
		// Skip IPv6 if not requested
		if !tf.showIPv6 && strings.Contains(ip, ":") {
			continue
		}
		addresses = append(addresses, ip)
	}

	if len(addresses) == 0 {
		return "-"
	}

	return strings.Join(addresses, ", ")
}

// PrintTable prints the interfaces table to stdout
func (tf *TableFormatter) PrintTable(collection *models.InterfaceCollection) {
	tf.FormatInterfacesTable(collection)
}

// PrintSummary prints a summary of the interfaces
func (tf *TableFormatter) PrintSummary(collection *models.InterfaceCollection) {
	total := len(collection.Interfaces)
	up := 0
	down := 0
	physical := 0
	virtual := 0

	for _, iface := range collection.Interfaces {
		if iface.IsUp() {
			up++
		} else {
			down++
		}

		if iface.InterfaceType == models.InterfaceTypePHYSICAL {
			physical++
		} else {
			virtual++
		}
	}

	fmt.Printf("\nSummary:\n")
	fmt.Printf("  Total Interfaces: %d\n", total)
	fmt.Printf("  Up: %d\n", up)
	fmt.Printf("  Down: %d\n", down)
	fmt.Printf("  Physical: %d\n", physical)
	fmt.Printf("  Virtual: %d\n", virtual)
} 