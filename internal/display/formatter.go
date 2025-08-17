package display

import (
	"fmt"
	"net"
	"os"
	"sort"
	"strconv"
	"strings"

	"github.com/olekukonko/tablewriter"
	"netgrid/internal/models"
)

// TableFormatter handles formatting of network interface tables
type TableFormatter struct {
	colorManager *ColorManager
}

// NewTableFormatter creates a new table formatter
func NewTableFormatter(colorScheme ColorScheme) *TableFormatter {
	return &TableFormatter{
		colorManager: NewColorManager(colorScheme),
	}
}

// SortBy represents different sorting options
type SortBy string

const (
	SortByName   SortBy = "name"
	SortByState  SortBy = "state"
	SortBySpeed  SortBy = "speed"
	SortByMAC    SortBy = "mac"
	SortByVendor SortBy = "vendor"
	SortByIP     SortBy = "ip"
)

// FormatOptions contains options for table formatting
type FormatOptions struct {
	ShowVendors bool
	ShowIPv6    bool
	ShowSummary bool
	SortBy      SortBy
}

// PrintTable prints a formatted table of network interfaces
func (tf *TableFormatter) PrintTable(interfaces []models.NetworkInterface, options FormatOptions) {
	// Sort interfaces
	sortedInterfaces := tf.sortInterfaces(interfaces, options.SortBy)

	// Create table
	table := tablewriter.NewWriter(os.Stdout)
	tf.configureTable(table, options)

	// Add header row with application name and description
	tf.addTitleRow(table, options)

	// Add rows
	for _, iface := range sortedInterfaces {
		row := tf.formatInterfaceRow(iface, options)
		table.Append(row)
	}

	table.Render()

	// Print summary if requested
	if options.ShowSummary {
		fmt.Println()
		tf.printSummary(interfaces)
	}
}

// configureTable sets up the table appearance and headers
func (tf *TableFormatter) configureTable(table *tablewriter.Table, options FormatOptions) {
	// Define headers
	headers := []string{"State", "Name", "Speed", "MAC", "MTU", "IP Config"}
	
	if options.ShowVendors {
		headers = append(headers, "Vendor")
	}
	
	headers = append(headers, "IP Addresses")

	// Apply colors to headers
	coloredHeaders := make([]string, len(headers))
	for i, header := range headers {
		coloredHeaders[i] = tf.colorManager.FormatHeader(header)
	}

	table.SetHeader(coloredHeaders)

	// Configure table appearance
	table.SetBorder(true)
	table.SetRowLine(false)  // Remove row lines for compactness
	table.SetCenterSeparator(tf.colorManager.Colorize("┼", "border"))
	table.SetColumnSeparator(tf.colorManager.Colorize("│", "border"))
	table.SetRowSeparator(tf.colorManager.Colorize("─", "border"))
	table.SetHeaderLine(true)
	table.SetAlignment(tablewriter.ALIGN_LEFT)
	
	// Set column alignment
	alignments := []int{
		tablewriter.ALIGN_CENTER, // State
		tablewriter.ALIGN_LEFT,   // Name
		tablewriter.ALIGN_CENTER, // Speed
		tablewriter.ALIGN_LEFT,   // MAC
		tablewriter.ALIGN_CENTER, // MTU
		tablewriter.ALIGN_CENTER, // IP Config
	}
	
	if options.ShowVendors {
		alignments = append(alignments, tablewriter.ALIGN_LEFT) // Vendor
	}
	
	alignments = append(alignments, tablewriter.ALIGN_LEFT) // IP Addresses
	
	table.SetColumnAlignment(alignments)
}

// addTitleRow adds a title row to the table with NetGrid name and description
func (tf *TableFormatter) addTitleRow(table *tablewriter.Table, options FormatOptions) {
	// Calculate total columns
	columnCount := 6 // State, Name, Speed, MAC, MTU, IP Config
	if options.ShowVendors {
		columnCount++
	}
	columnCount++ // IP Addresses
	
	// Create title row that spans all columns
	titleRow := make([]string, columnCount)
	// Place title in the middle columns to center it better
	centerCol := columnCount / 2
	titleRow[centerCol] = tf.colorManager.FormatTitle("NetGrid - Network Interface Information")
	for i := 0; i < columnCount; i++ {
		if i != centerCol {
			titleRow[i] = ""
		}
	}
	
	table.Append(titleRow)
}

// formatInterfaceRow formats a single interface as a table row
func (tf *TableFormatter) formatInterfaceRow(iface models.NetworkInterface, options FormatOptions) []string {
	// State indicator (just the colored circle)
	var state string
	if iface.IsUp() {
		state = tf.colorManager.Colorize("●", "up")
	} else {
		state = tf.colorManager.Colorize("●", "down")
	}

	// Interface name (just the name, no status indicator)
	name := iface.Name

	// Speed
	speed := tf.formatSpeedValue(iface)

	// MAC address
	mac := tf.formatMACValue(iface)

	// MTU
	mtu := tf.formatMTUValue(iface)

	// IP Config
	ipConfig := tf.formatIPConfigValue(iface)

	// Build row
	row := []string{state, name, speed, mac, mtu, ipConfig}

	// Vendor (if enabled)
	if options.ShowVendors {
		vendor := tf.formatVendorValue(iface)
		row = append(row, vendor)
	}

	// IP addresses
	ipAddresses := tf.formatIPAddresses(iface, options.ShowIPv6)
	row = append(row, ipAddresses)

	return row
}

// formatSpeedValue formats the speed column
func (tf *TableFormatter) formatSpeedValue(iface models.NetworkInterface) string {
	speedStr := iface.FormatSpeed()
	if speedStr == "-" {
		return tf.colorManager.FormatDim("-")
	}
	return tf.colorManager.FormatSpeed(speedStr)
}

// formatMACValue formats the MAC address column
func (tf *TableFormatter) formatMACValue(iface models.NetworkInterface) string {
	if iface.MACAddress == "" {
		return tf.colorManager.FormatDim("-")
	}
	return tf.colorManager.FormatMACAddress(iface.MACAddress)
}

// formatMTUValue formats the MTU column
func (tf *TableFormatter) formatMTUValue(iface models.NetworkInterface) string {
	if iface.MTU == nil {
		return tf.colorManager.FormatDim("-")
	}
	return strconv.Itoa(*iface.MTU)
}

// formatIPConfigValue formats the IP configuration column
func (tf *TableFormatter) formatIPConfigValue(iface models.NetworkInterface) string {
	if iface.IPConfigType == "" || iface.IPConfigType == "Unknown" {
		return tf.colorManager.FormatDim("-")
	}
	return iface.IPConfigType
}

// formatVendorValue formats the vendor column
func (tf *TableFormatter) formatVendorValue(iface models.NetworkInterface) string {
	if iface.Vendor == "" {
		return tf.colorManager.FormatDim("-")
	}
	return tf.colorManager.FormatVendor(iface.Vendor)
}

// formatIPAddresses formats the IP addresses column
func (tf *TableFormatter) formatIPAddresses(iface models.NetworkInterface, showIPv6 bool) string {
	if len(iface.IPAddresses) == 0 {
		return tf.colorManager.FormatDim("-")
	}

	var formattedIPs []string

	// Add IPv4 addresses
	ipv4s := iface.GetIPv4Addresses()
	for _, ip := range ipv4s {
		formattedIPs = append(formattedIPs, tf.colorManager.FormatIPAddress(ip, false))
	}

	// Add IPv6 addresses if requested
	if showIPv6 {
		ipv6s := iface.GetIPv6Addresses()
		for _, ip := range ipv6s {
			formattedIPs = append(formattedIPs, tf.colorManager.FormatIPAddress(ip, true))
		}
	}

	if len(formattedIPs) == 0 {
		return tf.colorManager.FormatDim("-")
	}

	return strings.Join(formattedIPs, ", ")
}

// sortInterfaces sorts interfaces according to the specified criteria
func (tf *TableFormatter) sortInterfaces(interfaces []models.NetworkInterface, sortBy SortBy) []models.NetworkInterface {
	sorted := make([]models.NetworkInterface, len(interfaces))
	copy(sorted, interfaces)

	switch sortBy {
	case SortByName:
		sort.Slice(sorted, func(i, j int) bool {
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		})
	case SortByState:
		sort.Slice(sorted, func(i, j int) bool {
			// UP interfaces first, then by name
			if sorted[i].IsUp() != sorted[j].IsUp() {
				return sorted[i].IsUp()
			}
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		})
	case SortBySpeed:
		sort.Slice(sorted, func(i, j int) bool {
			speedI := 0
			if sorted[i].Speed != nil {
				speedI = *sorted[i].Speed
			}
			speedJ := 0
			if sorted[j].Speed != nil {
				speedJ = *sorted[j].Speed
			}
			if speedI != speedJ {
				return speedI > speedJ // Higher speed first
			}
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		})
	case SortByMAC:
		sort.Slice(sorted, func(i, j int) bool {
			return sorted[i].MACAddress < sorted[j].MACAddress
		})
	case SortByVendor:
		sort.Slice(sorted, func(i, j int) bool {
			if sorted[i].Vendor != sorted[j].Vendor {
				return sorted[i].Vendor < sorted[j].Vendor
			}
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		})
	case SortByIP:
		sort.Slice(sorted, func(i, j int) bool {
			ipI := sorted[i].PrimaryIP()
			ipJ := sorted[j].PrimaryIP()
			if ipI != ipJ {
				// Convert IPs to comparable format
				return tf.compareIPs(ipI, ipJ)
			}
			return strings.ToLower(sorted[i].Name) < strings.ToLower(sorted[j].Name)
		})
	}

	return sorted
}

// compareIPs compares two IP addresses for sorting
func (tf *TableFormatter) compareIPs(ip1, ip2 string) bool {
	if ip1 == "" && ip2 == "" {
		return false
	}
	if ip1 == "" {
		return false
	}
	if ip2 == "" {
		return true
	}

	// Parse IPs for proper comparison
	parsed1 := net.ParseIP(ip1)
	parsed2 := net.ParseIP(ip2)
	
	if parsed1 == nil && parsed2 == nil {
		return ip1 < ip2
	}
	if parsed1 == nil {
		return false
	}
	if parsed2 == nil {
		return true
	}

	// Compare byte representation
	bytes1 := []byte(parsed1)
	bytes2 := []byte(parsed2)
	
	for i := 0; i < len(bytes1) && i < len(bytes2); i++ {
		if bytes1[i] != bytes2[i] {
			return bytes1[i] < bytes2[i]
		}
	}
	
	return len(bytes1) < len(bytes2)
}

// printSummary prints a summary of interface statistics
func (tf *TableFormatter) printSummary(interfaces []models.NetworkInterface) {
	total := len(interfaces)
	up := 0
	down := 0
	ethernet := 0
	wireless := 0
	other := 0

	for _, iface := range interfaces {
		if iface.IsUp() {
			up++
		} else {
			down++
		}

		name := strings.ToLower(iface.Name)
		switch {
		case strings.HasPrefix(name, "eno") || strings.HasPrefix(name, "ens") || strings.HasPrefix(name, "eth"):
			ethernet++
		case strings.HasPrefix(name, "wlan") || strings.HasPrefix(name, "wifi"):
			wireless++
		default:
			other++
		}
	}

	// Create summary table
	summaryTable := tablewriter.NewWriter(os.Stdout)
	summaryTable.SetHeader([]string{
		tf.colorManager.FormatHeader("Metric"),
		tf.colorManager.FormatHeader("Count"),
	})

	summaryTable.SetBorder(true)
	summaryTable.SetRowLine(false)  // Remove row lines for compactness
	summaryTable.SetCenterSeparator(tf.colorManager.Colorize("┼", "border"))
	summaryTable.SetColumnSeparator(tf.colorManager.Colorize("│", "border"))
	summaryTable.SetRowSeparator(tf.colorManager.Colorize("─", "border"))
	summaryTable.SetHeaderLine(true)
	summaryTable.SetAlignment(tablewriter.ALIGN_LEFT)

	// Add summary rows
	summaryTable.Append([]string{"Total Interfaces", strconv.Itoa(total)})
	summaryTable.Append([]string{"Up", tf.colorManager.Colorize(strconv.Itoa(up), "up")})
	summaryTable.Append([]string{"Down", tf.colorManager.Colorize(strconv.Itoa(down), "down")})
	summaryTable.Append([]string{"Ethernet", strconv.Itoa(ethernet)})
	summaryTable.Append([]string{"Wireless", strconv.Itoa(wireless)})
	summaryTable.Append([]string{"Other", strconv.Itoa(other)})

	// Print title for summary
	fmt.Println(tf.colorManager.FormatTitle("Interface Summary"))
	summaryTable.Render()
}

// PrintError prints an error message
func (tf *TableFormatter) PrintError(message string) {
	fmt.Println(tf.colorManager.FormatError(message))
}

// PrintWarning prints a warning message
func (tf *TableFormatter) PrintWarning(message string) {
	fmt.Println(tf.colorManager.FormatWarning(message))
}

// PrintInfo prints an info message
func (tf *TableFormatter) PrintInfo(message string) {
	fmt.Println(tf.colorManager.FormatInfo(message))
}

// PrintSuccess prints a success message
func (tf *TableFormatter) PrintSuccess(message string) {
	fmt.Println(tf.colorManager.FormatSuccess(message))
}