"""
Vendor lookup module for NetGrid.

This module provides functionality to look up vendor information for MAC addresses
using OUI (Organizationally Unique Identifier) databases with local caching.
"""

import os
import json
import hashlib
import requests
from typing import Optional, Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VendorLookup:
    """
    Handles vendor lookups for MAC addresses using OUI databases.
    
    Supports multiple lookup sources and local caching for performance.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the vendor lookup system.
        
        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.netgrid/cache
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.netgrid/cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.oui_cache_file = self.cache_dir / "oui_cache.json"
        self.vendor_cache_file = self.cache_dir / "vendor_cache.json"
        
        # Load existing caches
        self.oui_cache = self._load_cache(self.oui_cache_file)
        self.vendor_cache = self._load_cache(self.vendor_cache_file)
        
        # OUI database sources (updated with more reliable sources)
        self.oui_sources = [
            "https://raw.githubusercontent.com/wireshark/wireshark/master/manuf",
            "https://standards-oui.ieee.org/oui/oui.csv",
            "https://api.macvendors.com/",  # API endpoint
            "https://macvendors.co/api/",   # Alternative API
        ]
    
    def _load_cache(self, cache_file: Path) -> Dict[str, str]:
        """Load cache from file."""
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache from {cache_file}: {e}")
        return {}
    
    def _save_cache(self, cache_file: Path, cache_data: Dict[str, str]) -> None:
        """Save cache to file."""
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save cache to {cache_file}: {e}")
    
    def _normalize_mac(self, mac: str) -> str:
        """
        Normalize MAC address to uppercase without separators.
        
        Args:
            mac: MAC address string
            
        Returns:
            Normalized MAC address (e.g., "C4346BBA796C")
        """
        # Remove common separators and convert to uppercase
        normalized = mac.replace(':', '').replace('-', '').replace('.', '').upper()
        
        # Validate MAC address format (should be 12 hex characters)
        if len(normalized) != 12 or not all(c in '0123456789ABCDEF' for c in normalized):
            raise ValueError(f"Invalid MAC address format: {mac}")
        
        return normalized
    
    def _extract_oui(self, mac: str) -> str:
        """
        Extract OUI (first 6 characters) from MAC address.
        
        Args:
            mac: Normalized MAC address
            
        Returns:
            OUI string (first 6 characters)
        """
        return mac[:6]
    
    def lookup_vendor(self, mac: str) -> Optional[str]:
        """
        Look up vendor information for a MAC address.
        
        Args:
            mac: MAC address string
            
        Returns:
            Vendor name if found, None otherwise
        """
        try:
            normalized_mac = self._normalize_mac(mac)
            oui = self._extract_oui(normalized_mac)
            
            # Check cache first
            if oui in self.vendor_cache:
                return self.vendor_cache[oui]
            
            # Try to find vendor
            vendor = self._find_vendor(oui)
            
            # Cache the result (even if None to avoid repeated lookups)
            self.vendor_cache[oui] = vendor
            self._save_cache(self.vendor_cache_file, self.vendor_cache)
            
            return vendor
            
        except ValueError as e:
            logger.warning(f"Invalid MAC address: {mac} - {e}")
            return None
        except Exception as e:
            logger.error(f"Error looking up vendor for {mac}: {e}")
            return None
    
    def _find_vendor(self, oui: str) -> Optional[str]:
        """
        Find vendor information for an OUI.
        
        Args:
            oui: OUI string (6 hex characters)
            
        Returns:
            Vendor name if found, None otherwise
        """
        # Check local OUI cache first
        if oui in self.oui_cache:
            return self.oui_cache[oui]
        
        # Try to fetch from online sources
        vendor = self._fetch_vendor_online(oui)
        if vendor:
            self.oui_cache[oui] = vendor
            self._save_cache(self.oui_cache_file, self.oui_cache)
        
        return vendor
    
    def _fetch_vendor_online(self, oui: str) -> Optional[str]:
        """
        Fetch vendor information from online sources.
        
        Args:
            oui: OUI string
            
        Returns:
            Vendor name if found, None otherwise
        """
        for source_url in self.oui_sources:
            try:
                vendor = self._fetch_from_source(source_url, oui)
                if vendor:
                    return vendor
            except Exception as e:
                logger.debug(f"Failed to fetch from {source_url}: {e}")
                continue
        
        return None
    
    def _fetch_from_source(self, source_url: str, oui: str) -> Optional[str]:
        """
        Fetch vendor information from a specific source.
        
        Args:
            source_url: URL of the OUI database
            oui: OUI string to look up
            
        Returns:
            Vendor name if found, None otherwise
        """
        try:
            # Handle API endpoints differently
            if "api.macvendors.com" in source_url or "macvendors.co/api" in source_url:
                # API endpoints expect full MAC address
                mac_address = f"{oui[:2]}:{oui[2:4]}:{oui[4:6]}:00:00:00"
                api_url = source_url.rstrip('/') + '/' + mac_address
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    return response.text.strip()
                return None
            
            # Handle database files
            response = requests.get(source_url, timeout=10)
            response.raise_for_status()
            
            # Parse different source formats
            if "manuf" in source_url:
                return self._parse_manuf_format(response.text, oui)
            elif "oui.csv" in source_url:
                return self._parse_csv_format(response.text, oui)
            
        except Exception as e:
            logger.debug(f"Error fetching from {source_url}: {e}")
        
        return None
    
    def _parse_manuf_format(self, content: str, oui: str) -> Optional[str]:
        """Parse Wireshark manuf format."""
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('\t')
                if len(parts) >= 2:
                    if parts[0].upper().replace(':', '') == oui:
                        return parts[1].strip()
        return None
    
    def _parse_csv_format(self, content: str, oui: str) -> Optional[str]:
        """Parse IEEE CSV format."""
        for line in content.split('\n'):
            if line.strip() and not line.startswith('Registry'):
                parts = line.split(',')
                if len(parts) >= 3:
                    if parts[1].upper().replace(':', '') == oui:
                        return parts[2].strip().strip('"')
        return None
    
    def bulk_lookup(self, mac_addresses: List[str]) -> Dict[str, Optional[str]]:
        """
        Perform bulk vendor lookups for multiple MAC addresses.
        
        Args:
            mac_addresses: List of MAC address strings
            
        Returns:
            Dictionary mapping MAC addresses to vendor names
        """
        results = {}
        for mac in mac_addresses:
            try:
                results[mac] = self.lookup_vendor(mac)
            except Exception as e:
                logger.warning(f"Failed to lookup vendor for {mac}: {e}")
                results[mac] = None
        return results
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.oui_cache.clear()
        self.vendor_cache.clear()
        
        if self.oui_cache_file.exists():
            self.oui_cache_file.unlink()
        if self.vendor_cache_file.exists():
            self.vendor_cache_file.unlink()
        
        logger.info("Vendor lookup cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache sizes
        """
        return {
            'oui_cache_size': len(self.oui_cache),
            'vendor_cache_size': len(self.vendor_cache)
        } 