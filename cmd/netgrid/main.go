package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"netgrid/internal/collector"
	"netgrid/internal/display"
	"netgrid/internal/models"
)

var (
	// Command line flags
	showIPv6       bool
	noVendors      bool
	includeVirtual bool
	showSummary    bool
	sortBy         string
	colorScheme    string
)

func main() {
	var rootCmd = &cobra.Command{
		Use:   "netgrid",
		Short: "NetGrid - Network interface information tool",
		Long: `NetGrid displays up-to-date network interface information in a beautiful table format.

It shows interface status, IP addresses, MAC addresses, speed, vendor information, and more.`,
		Run: runNetGrid,
	}

	// Add flags
	rootCmd.Flags().BoolVar(&showIPv6, "show-ipv6", false, "Show IPv6 addresses in addition to IPv4")
	rootCmd.Flags().BoolVar(&noVendors, "no-vendors", false, "Disable vendor lookup")
	rootCmd.Flags().BoolVar(&includeVirtual, "include-virtual", false, "Include virtual interfaces (veth, br-, lo, tailscale, etc.)")
	rootCmd.Flags().BoolVar(&showSummary, "show-summary", false, "Show interface summary")
	rootCmd.Flags().StringVar(&sortBy, "sort-by", "name", "Sort by column (name, state, speed, mac, vendor, ip)")
	rootCmd.Flags().StringVar(&colorScheme, "color-scheme", "default", "Color scheme to use (default, dark, light, high_contrast, colorblind)")

	// Execute the command
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}

func runNetGrid(cmd *cobra.Command, args []string) {
	// Validate color scheme
	validSchemes := display.GetAvailableSchemes()
	if !contains(validSchemes, colorScheme) {
		fmt.Fprintf(os.Stderr, "Error: Invalid color scheme '%s'. Available schemes: %s\n", 
			colorScheme, strings.Join(validSchemes, ", "))
		os.Exit(1)
	}

	// Validate sort option
	validSortOptions := []string{"name", "state", "speed", "mac", "vendor", "ip"}
	if !contains(validSortOptions, sortBy) {
		fmt.Fprintf(os.Stderr, "Error: Invalid sort option '%s'. Available options: %s\n", 
			sortBy, strings.Join(validSortOptions, ", "))
		os.Exit(1)
	}

	// Create formatter
	formatter := display.NewTableFormatter(display.ColorScheme(colorScheme))

	// Create interface collector
	interfaceCollector := collector.NewInterfaceCollector(!noVendors)

	// Collect interface information
	interfaces, err := interfaceCollector.GetAllInterfaces()
	if err != nil {
		formatter.PrintError(fmt.Sprintf("Failed to collect interface information: %v", err))
		os.Exit(1)
	}

	// Filter interfaces if needed
	var finalInterfaces []models.NetworkInterface
	if includeVirtual {
		finalInterfaces = interfaces
	} else {
		// Filter out virtual interfaces
		finalInterfaces = collector.FilterNonVirtual(interfaces)
	}

	// Check if we have any interfaces to display
	if len(finalInterfaces) == 0 {
		formatter.PrintWarning("No network interfaces found (after filtering)")
		return
	}

	// Set up format options
	options := display.FormatOptions{
		ShowVendors: !noVendors,
		ShowIPv6:    showIPv6,
		ShowSummary: showSummary,
		SortBy:      display.SortBy(sortBy),
	}

	// Print the table
	formatter.PrintTable(finalInterfaces, options)
}

// contains checks if a slice contains a string
func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}