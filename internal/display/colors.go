package display

import (
	"github.com/fatih/color"
)

// ColorScheme represents different color schemes
type ColorScheme string

const (
	ColorSchemeDefault      ColorScheme = "default"
	ColorSchemeDark        ColorScheme = "dark"
	ColorSchemeLight       ColorScheme = "light"
	ColorSchemeHighContrast ColorScheme = "high_contrast"
	ColorSchemeColorblind  ColorScheme = "colorblind"
)

// ColorManager manages color schemes and formatting
type ColorManager struct {
	scheme ColorScheme
	colors map[string]*color.Color
}

// NewColorManager creates a new color manager with the specified scheme
func NewColorManager(scheme ColorScheme) *ColorManager {
	cm := &ColorManager{
		scheme: scheme,
		colors: make(map[string]*color.Color),
	}
	cm.initializeColors()
	return cm
}

// initializeColors sets up the color definitions for the current scheme
func (cm *ColorManager) initializeColors() {
	switch cm.scheme {
	case ColorSchemeDark:
		cm.initializeDarkColors()
	case ColorSchemeLight:
		cm.initializeLightColors()
	case ColorSchemeHighContrast:
		cm.initializeHighContrastColors()
	case ColorSchemeColorblind:
		cm.initializeColorblindColors()
	default:
		cm.initializeDefaultColors()
	}
}

func (cm *ColorManager) initializeDefaultColors() {
	// Interface states
	cm.colors["up"] = color.New(color.FgGreen, color.Bold)
	cm.colors["down"] = color.New(color.FgRed, color.Bold)
	cm.colors["unknown"] = color.New(color.FgYellow)

	// Interface types
	cm.colors["ethernet"] = color.New(color.FgBlue)
	cm.colors["wireless"] = color.New(color.FgMagenta)
	cm.colors["virtual"] = color.New(color.FgCyan)
	cm.colors["loopback"] = color.New(color.FgWhite)

	// Data types
	cm.colors["ipv4"] = color.New(color.FgGreen)
	cm.colors["ipv6"] = color.New(color.FgCyan)
	cm.colors["mac"] = color.New(color.FgBlue)
	cm.colors["vendor"] = color.New(color.FgMagenta)
	cm.colors["speed"] = color.New(color.FgYellow)

	// UI elements
	cm.colors["title"] = color.New(color.FgBlue, color.Bold)
	cm.colors["header"] = color.New(color.FgMagenta, color.Bold)
	cm.colors["border"] = color.New(color.FgBlue)
	cm.colors["error"] = color.New(color.FgRed, color.Bold)
	cm.colors["warning"] = color.New(color.FgYellow, color.Bold)
	cm.colors["info"] = color.New(color.FgBlue, color.Bold)
	cm.colors["success"] = color.New(color.FgGreen, color.Bold)

	// Text emphasis
	cm.colors["bold"] = color.New(color.Bold)
	cm.colors["dim"] = color.New(color.Faint)
	cm.colors["normal"] = color.New()
}

func (cm *ColorManager) initializeDarkColors() {
	// Interface states
	cm.colors["up"] = color.New(color.FgHiGreen, color.Bold)
	cm.colors["down"] = color.New(color.FgHiRed, color.Bold)
	cm.colors["unknown"] = color.New(color.FgHiYellow)

	// Interface types
	cm.colors["ethernet"] = color.New(color.FgHiBlue)
	cm.colors["wireless"] = color.New(color.FgHiMagenta)
	cm.colors["virtual"] = color.New(color.FgHiCyan)
	cm.colors["loopback"] = color.New(color.FgHiWhite)

	// Data types
	cm.colors["ipv4"] = color.New(color.FgHiGreen)
	cm.colors["ipv6"] = color.New(color.FgHiCyan)
	cm.colors["mac"] = color.New(color.FgHiBlue)
	cm.colors["vendor"] = color.New(color.FgHiMagenta)
	cm.colors["speed"] = color.New(color.FgHiYellow)

	// UI elements
	cm.colors["title"] = color.New(color.FgHiBlue, color.Bold)
	cm.colors["header"] = color.New(color.FgHiMagenta, color.Bold)
	cm.colors["border"] = color.New(color.FgHiBlue)
	cm.colors["error"] = color.New(color.FgHiRed, color.Bold)
	cm.colors["warning"] = color.New(color.FgHiYellow, color.Bold)
	cm.colors["info"] = color.New(color.FgHiBlue, color.Bold)
	cm.colors["success"] = color.New(color.FgHiGreen, color.Bold)

	// Text emphasis
	cm.colors["bold"] = color.New(color.Bold)
	cm.colors["dim"] = color.New(color.Faint)
	cm.colors["normal"] = color.New()
}

func (cm *ColorManager) initializeLightColors() {
	// Interface states
	cm.colors["up"] = color.New(color.FgGreen, color.Bold)
	cm.colors["down"] = color.New(color.FgRed, color.Bold)
	cm.colors["unknown"] = color.New(color.FgYellow, color.Bold)

	// Interface types
	cm.colors["ethernet"] = color.New(color.FgBlue, color.Bold)
	cm.colors["wireless"] = color.New(color.FgMagenta, color.Bold)
	cm.colors["virtual"] = color.New(color.FgCyan, color.Bold)
	cm.colors["loopback"] = color.New(color.FgBlack, color.Bold)

	// Data types
	cm.colors["ipv4"] = color.New(color.FgGreen, color.Bold)
	cm.colors["ipv6"] = color.New(color.FgCyan, color.Bold)
	cm.colors["mac"] = color.New(color.FgBlue, color.Bold)
	cm.colors["vendor"] = color.New(color.FgMagenta, color.Bold)
	cm.colors["speed"] = color.New(color.FgYellow, color.Bold)

	// UI elements
	cm.colors["title"] = color.New(color.FgBlue, color.Bold)
	cm.colors["header"] = color.New(color.FgMagenta, color.Bold)
	cm.colors["border"] = color.New(color.FgBlue, color.Bold)
	cm.colors["error"] = color.New(color.FgRed, color.Bold)
	cm.colors["warning"] = color.New(color.FgYellow, color.Bold)
	cm.colors["info"] = color.New(color.FgBlue, color.Bold)
	cm.colors["success"] = color.New(color.FgGreen, color.Bold)

	// Text emphasis
	cm.colors["bold"] = color.New(color.Bold)
	cm.colors["dim"] = color.New(color.Faint)
	cm.colors["normal"] = color.New()
}

func (cm *ColorManager) initializeHighContrastColors() {
	// Interface states
	cm.colors["up"] = color.New(color.FgHiGreen, color.Bold)
	cm.colors["down"] = color.New(color.FgHiRed, color.Bold)
	cm.colors["unknown"] = color.New(color.FgHiYellow, color.Bold)

	// Interface types
	cm.colors["ethernet"] = color.New(color.FgHiWhite, color.Bold)
	cm.colors["wireless"] = color.New(color.FgHiWhite, color.Bold)
	cm.colors["virtual"] = color.New(color.FgHiWhite, color.Bold)
	cm.colors["loopback"] = color.New(color.FgHiWhite, color.Bold)

	// Data types
	cm.colors["ipv4"] = color.New(color.FgHiGreen, color.Bold)
	cm.colors["ipv6"] = color.New(color.FgHiCyan, color.Bold)
	cm.colors["mac"] = color.New(color.FgHiWhite, color.Bold)
	cm.colors["vendor"] = color.New(color.FgHiWhite, color.Bold)
	cm.colors["speed"] = color.New(color.FgHiYellow, color.Bold)

	// UI elements
	cm.colors["title"] = color.New(color.FgHiWhite, color.Bold)
	cm.colors["header"] = color.New(color.FgHiWhite, color.Bold)
	cm.colors["border"] = color.New(color.FgHiWhite, color.Bold)
	cm.colors["error"] = color.New(color.FgHiRed, color.Bold)
	cm.colors["warning"] = color.New(color.FgHiYellow, color.Bold)
	cm.colors["info"] = color.New(color.FgHiCyan, color.Bold)
	cm.colors["success"] = color.New(color.FgHiGreen, color.Bold)

	// Text emphasis
	cm.colors["bold"] = color.New(color.Bold)
	cm.colors["dim"] = color.New(color.Faint)
	cm.colors["normal"] = color.New()
}

func (cm *ColorManager) initializeColorblindColors() {
	// Same as default but relies more on symbols and contrast
	cm.initializeDefaultColors()
}

// Colorize applies the specified color to text
func (cm *ColorManager) Colorize(text string, colorName string) string {
	if colorFunc, exists := cm.colors[colorName]; exists {
		return colorFunc.Sprint(text)
	}
	return text
}

// FormatInterfaceState formats interface state with appropriate color and symbol
func (cm *ColorManager) FormatInterfaceState(isUp bool, name string) string {
	if isUp {
		return cm.Colorize("● "+name, "up")
	}
	return cm.Colorize("● "+name, "down")
}

// FormatIPAddress formats IP address with appropriate color
func (cm *ColorManager) FormatIPAddress(ip string, isIPv6 bool) string {
	colorName := "ipv4"
	if isIPv6 {
		colorName = "ipv6"
	}
	return cm.Colorize(ip, colorName)
}

// FormatMACAddress formats MAC address with appropriate color
func (cm *ColorManager) FormatMACAddress(mac string) string {
	return cm.Colorize(mac, "mac")
}

// FormatVendor formats vendor name with appropriate color
func (cm *ColorManager) FormatVendor(vendor string) string {
	return cm.Colorize(vendor, "vendor")
}

// FormatSpeed formats speed with appropriate color
func (cm *ColorManager) FormatSpeed(speed string) string {
	return cm.Colorize(speed, "speed")
}

// FormatDim formats text as dimmed
func (cm *ColorManager) FormatDim(text string) string {
	return cm.Colorize(text, "dim")
}

// FormatBold formats text as bold
func (cm *ColorManager) FormatBold(text string) string {
	return cm.Colorize(text, "bold")
}

// FormatTitle formats text as a title
func (cm *ColorManager) FormatTitle(text string) string {
	return cm.Colorize(text, "title")
}

// FormatHeader formats text as a header
func (cm *ColorManager) FormatHeader(text string) string {
	return cm.Colorize(text, "header")
}

// FormatError formats error message
func (cm *ColorManager) FormatError(text string) string {
	return cm.Colorize("Error: "+text, "error")
}

// FormatWarning formats warning message
func (cm *ColorManager) FormatWarning(text string) string {
	return cm.Colorize("Warning: "+text, "warning")
}

// FormatInfo formats info message
func (cm *ColorManager) FormatInfo(text string) string {
	return cm.Colorize("Info: "+text, "info")
}

// FormatSuccess formats success message
func (cm *ColorManager) FormatSuccess(text string) string {
	return cm.Colorize(text, "success")
}

// GetAvailableSchemes returns a list of available color schemes
func GetAvailableSchemes() []string {
	return []string{
		string(ColorSchemeDefault),
		string(ColorSchemeDark),
		string(ColorSchemeLight),
		string(ColorSchemeHighContrast),
		string(ColorSchemeColorblind),
	}
}