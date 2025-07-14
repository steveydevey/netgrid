package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/netgrid/netgrid-go/internal/collector"
	"github.com/netgrid/netgrid-go/internal/display"
	"github.com/netgrid/netgrid-go/internal/models"
)

var (
	cfgFile string
	showIPv6 bool
	noVendors bool
	includeVirtual bool
	showSummary bool
	sortBy string
	colorScheme string
)

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "netgrid-go",
	Short: "NetGrid Go: Display network interface information in a table format",
	Long: `NetGrid Go is a high-performance command line tool for displaying 
network interface information in a visual table format.

Features:
- Real-time network interface discovery
- Vendor lookup with caching
- Colored output with multiple themes
- Sorting and filtering options
- IPv6 support
- Virtual interface filtering`,
	Run: runNetGrid,
}

// Execute adds all child commands to the root command and sets flags appropriately.
func Execute() error {
	return rootCmd.Execute()
}

func init() {
	cobra.OnInitialize(initConfig)

	// Global flags
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.netgrid-go.yaml)")
	
	// Local flags
	rootCmd.Flags().BoolVar(&showIPv6, "show-ipv6", false, "Show IPv6 addresses in addition to IPv4")
	rootCmd.Flags().BoolVar(&noVendors, "no-vendors", false, "Disable vendor lookup")
	rootCmd.Flags().BoolVar(&includeVirtual, "include-virtual", false, "Include virtual interfaces (veth, br-, lo, tailscale, vmsgohere)")
	rootCmd.Flags().BoolVar(&showSummary, "show-summary", false, "Show interface summary")
	rootCmd.Flags().StringVar(&sortBy, "sort-by", "name", "Sort by column (name, state, speed, mac, vendor, ip)")
	rootCmd.Flags().StringVar(&colorScheme, "color-scheme", "default", "Color scheme to use (default, dark, light, high_contrast, colorblind)")
}

// initConfig reads in config file and ENV variables if set.
func initConfig() {
	if cfgFile != "" {
		// Use config file from the flag.
		viper.SetConfigFile(cfgFile)
	} else {
		// Find home directory.
		home, err := os.UserHomeDir()
		cobra.CheckErr(err)

		// Search config in home directory with name ".netgrid-go" (without extension).
		viper.AddConfigPath(home)
		viper.SetConfigType("yaml")
		viper.SetConfigName(".netgrid-go")
	}

	viper.AutomaticEnv() // read in environment variables that match

	// If a config file is found, read it in.
	if err := viper.ReadInConfig(); err == nil {
		fmt.Fprintln(os.Stderr, "Using config file:", viper.ConfigFileUsed())
	}
}

func runNetGrid(cmd *cobra.Command, args []string) {
	// Initialize collector
	collector := collector.NewInterfaceCollector(!noVendors)
	
	// Collect interfaces
	collection, err := collector.GetAllInterfaces()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error collecting interfaces: %v\n", err)
		os.Exit(1)
	}
	
	// Filter virtual interfaces if not requested
	if !includeVirtual {
		filtered := filterVirtualInterfaces(collection)
		collection = filtered
	}
	
	if len(collection.Interfaces) == 0 {
		fmt.Println("No network interfaces found (after filtering).")
		return
	}
	
	// Initialize table formatter
	formatter := display.NewTableFormatter(!noVendors, showIPv6, sortBy)
	
	// Display the table
	formatter.PrintTable(collection)
	
	// Show summary if requested
	if showSummary {
		formatter.PrintSummary(collection)
	}
}

// filterVirtualInterfaces filters out virtual interfaces from the collection
func filterVirtualInterfaces(collection *models.InterfaceCollection) *models.InterfaceCollection {
	filtered := models.NewInterfaceCollection()
	
	for _, iface := range collection.Interfaces {
		if !iface.IsVirtualInterface() {
			filtered.AddInterface(iface)
		}
	}
	
	return filtered
} 