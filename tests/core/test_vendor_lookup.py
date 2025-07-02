"""Tests for vendor lookup functionality."""

import pytest
import tempfile
from unittest.mock import patch, MagicMock
from netgrid.core.vendor_lookup import VendorLookup


def test_vendor_lookup_init():
    """Test VendorLookup initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vl = VendorLookup(cache_dir=temp_dir)
        assert str(vl.cache_dir) == temp_dir


def test_lookup_vendor_with_cache():
    """Test vendor lookup with cached result."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vl = VendorLookup(cache_dir=temp_dir)
        
        # Mock the vendor cache to return a known vendor
        vl.vendor_cache = {'C4346B': 'Test Vendor'}
        
        result = vl.lookup_vendor('C4:34:6B:BA:79:6C')
        assert result == 'Test Vendor'


def test_lookup_vendor_invalid_mac():
    """Test vendor lookup with invalid MAC address."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vl = VendorLookup(cache_dir=temp_dir)
        
        result = vl.lookup_vendor('invalid')
        assert result is None


def test_get_cache_stats():
    """Test cache statistics."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vl = VendorLookup(cache_dir=temp_dir)
        
        # Add some test data
        vl.oui_cache = {'test1': 'vendor1'}
        vl.vendor_cache = {'test2': 'vendor2', 'test3': 'vendor3'}
        
        stats = vl.get_cache_stats()
        
        assert stats['oui_cache_size'] == 1
        assert stats['vendor_cache_size'] == 2


def test_clear_cache():
    """Test cache clearing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vl = VendorLookup(cache_dir=temp_dir)
        
        # Add some test data
        vl.oui_cache = {'test1': 'vendor1'}
        vl.vendor_cache = {'test2': 'vendor2'}
        
        vl.clear_cache()
        
        assert len(vl.oui_cache) == 0
        assert len(vl.vendor_cache) == 0 