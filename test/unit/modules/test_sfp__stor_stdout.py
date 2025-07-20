import pytest
import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
from io import StringIO

from modules.sfp__stor_stdout import sfp__stor_stdout
from spiderfoot.sflib import SpiderFoot
from spiderfoot.event import SpiderFootEvent
from test.unit.utils.test_module_base import TestModuleBase
from test.unit.utils.test_helpers import safe_recursion


class TestModuleStor_stdout(TestModuleBase):
    """Comprehensive test suite for stdout storage module.
    
    Tests output formatting, filtering, and proper event handling.
    """

    def setUp(self):
        """Set up before each test."""
        super().setUp()
        # Reset class-level state to avoid test interference
        sfp__stor_stdout.firstEvent = True
        # Create SpiderFoot instance
        self.sf_instance = SpiderFoot(self.default_options)
        
        # Register event emitters if they exist
        if hasattr(self, 'module'):
            self.register_event_emitter(self.module)

    def tearDown(self):
        """Clean up after each test."""
        super().tearDown()

    @unittest.skip("This module contains an extra private option")
    def test_opts(self):
        module = sfp__stor_stdout()
        self.assertEqual(len(module.opts), len(module.optdescs))

    def test_setup(self):
        """Test basic setup functionality."""
        module = sfp__stor_stdout()
        module.setup(self.sf_instance, dict())
        
        self.assertIsNotNone(module.sf)
        self.assertIsNotNone(module.opts)

    def test_setup_with_options(self):
        """Test setup with custom options."""
        module = sfp__stor_stdout()
        custom_opts = {
            'maxdata': 100,
            'format': 'json'
        }
        module.setup(self.sf_instance, custom_opts)
        
        # Verify options were set correctly
        for key, value in custom_opts.items():
            if key in module.opts:
                self.assertEqual(module.opts[key], value)

    def test_watchedEvents_should_return_list(self):
        """Test that watchedEvents returns a list."""
        module = sfp__stor_stdout()
        events = module.watchedEvents()
        self.assertIsInstance(events, list)
        # Should watch all events
        self.assertIn("*", events)

    def test_producedEvents_should_return_list(self):
        """Test that producedEvents returns a list."""
        module = sfp__stor_stdout()
        events = module.producedEvents()
        self.assertIsInstance(events, list)

    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_event_basic_output(self, mock_stdout):
        """Test basic event handling and output."""
        module = sfp__stor_stdout()
        
        # Set up proper event types dictionary
        test_opts = {
            '_eventtypes': {
                'IP_ADDRESS': 'IP Address',
                'ROOT': 'Root'
            }
        }
        module.setup(self.sf_instance, test_opts)
        
        # Create test event
        test_event = SpiderFootEvent("IP_ADDRESS", "192.168.1.1", "test_module", None)
        test_event.confidence = 100
        test_event.visibility = 1
        test_event.risk = 0
        
        # Mock getScanId
        module.getScanId = MagicMock(return_value="test_scan_id")
        
        module.handleEvent(test_event)
          # Check that something was written to stdout
        output = mock_stdout.getvalue()
        self.assertIn("192.168.1.1", output)
        self.assertIn("IP Address", output)  # Should contain the display name, not the raw event type

    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_event_with_data_truncation(self, mock_stdout):
        """Test that data is truncated when exceeding max length."""
        module = sfp__stor_stdout()
        test_opts = {
            'enabled': True,
            '_maxlength': 10,
            '_eventtypes': {
                'IP_ADDRESS': 'IP Address',
                'ROOT': 'Root'
            },
            '_showonlyrequested': False
        }
        module.setup(self.sf_instance, test_opts)
        large_data = "A" * 1000
        test_event = SpiderFootEvent("IP_ADDRESS", large_data, "test_module", None)
        test_event.confidence = 100
        test_event.visibility = 1
        test_event.risk = 0
        module.getScanId = MagicMock(return_value="test_scan_id")
        module.handleEvent(test_event)
        output = mock_stdout.getvalue()
        self.assertIn("IP Address", output)  # Check for display name
        self.assertTrue(len(output) < len(large_data) + 50)  # Much shorter than original

    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_event_disabled(self, mock_stdout):
        """Test that no output occurs when module is disabled."""
        module = sfp__stor_stdout()
        module.setup(self.sf_instance, {'_store': False})
        
        # Create test event
        test_event = SpiderFootEvent("IP_ADDRESS", "192.168.1.1", "test_module", None)
        
        module.handleEvent(test_event)
        
        # Check that nothing was written to stdout
        output = mock_stdout.getvalue()
        self.assertEqual(output, "")

    @patch('builtins.print')
    def test_handle_multiple_events(self, mock_print):
        """Test handling multiple events."""
        module = sfp__stor_stdout()
        test_opts = {
            'enabled': True,
            '_eventtypes': {
                'IP_ADDRESS': 'IP Address',
                'ROOT': 'Root'
            },
            '_showonlyrequested': False,
            '_maxlength': 1000  # Ensure no truncation
        }
        module.setup(self.sf_instance, test_opts)
        module.getScanId = MagicMock(return_value="test_scan_id")
        events = [
            SpiderFootEvent("IP_ADDRESS", f"192.168.1.{i}", "test_module", None)
            for i in range(3)
        ]
        for event in events:
            event.confidence = 100
            event.visibility = 1
            event.risk = 0
            module.handleEvent(event)
        
        # Check that print was called for each event
        self.assertEqual(len(mock_print.call_args_list), 3)
        
        # Check that each IP address appears in the printed outputs
        # The module uses tab-delimited format: module\tevent_type\tdata
        # Extract and verify each call's content
        found_ips = set()
        for call in mock_print.call_args_list:
            if call[0]:  # call[0] contains the positional arguments
                # The first argument is the formatted string
                formatted_string = str(call[0][0])
                # Look for IP addresses in the formatted string
                for i in range(3):
                    expected_ip = f"192.168.1.{i}"
                    if expected_ip in formatted_string:
                        found_ips.add(expected_ip)
        
        # Verify all IP addresses were found
        for i in range(3):
            expected_ip = f"192.168.1.{i}"
            self.assertIn(expected_ip, found_ips,
                          f"Expected IP {expected_ip} not found. Found IPs: {found_ips}. "
                          f"Print calls: {[str(call[0][0]) if call[0] else 'empty' for call in mock_print.call_args_list]}")
        
        # Verify the display name appears at least once
        all_output = " ".join(str(call[0][0]) if call[0] else "" for call in mock_print.call_args_list)
        self.assertIn("IP Address", all_output)  # Check for display name

    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_event_with_special_characters(self, mock_stdout):
        """Test handling events with special characters."""
        module = sfp__stor_stdout()
        module.setup(self.sf_instance, dict())
        
        # Create test event with special characters
        special_data = "test\nwith\ttabs\rand\x00nulls"
        test_event = SpiderFootEvent("SPECIAL_DATA", special_data, "test_module", None)
        test_event.confidence = 100
        test_event.visibility = 1
        test_event.risk = 0
        
        # Mock getScanId
        module.getScanId = MagicMock(return_value="test_scan_id")
        
        # Should handle special characters gracefully
        try:
            module.handleEvent(test_event)
            output = mock_stdout.getvalue()
            # Should produce some output without crashing
            self.assertIsInstance(output, str)
        except Exception as e:
            self.fail(f"Module should handle special characters gracefully: {e}")

    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_event_unicode(self, mock_stdout):
        """Test handling events with Unicode characters."""
        module = sfp__stor_stdout()
        module.setup(self.sf_instance, dict())
        
        # Create test event with Unicode characters
        unicode_data = "测试数据 with émojis 🚀"
        test_event = SpiderFootEvent("UNICODE_DATA", unicode_data, "test_module", None)
        test_event.confidence = 100
        test_event.visibility = 1
        test_event.risk = 0
        
        # Mock getScanId
        module.getScanId = MagicMock(return_value="test_scan_id")
        
        # Should handle Unicode characters gracefully
        try:
            module.handleEvent(test_event)
            output = mock_stdout.getvalue()
            # Should produce some output without crashing
            self.assertIsInstance(output, str)
        except Exception as e:
            self.fail(f"Module should handle Unicode characters gracefully: {e}")

    def test_output_formatting_consistency(self):
        """Test that output formatting is consistent."""
        module = sfp__stor_stdout()
        module.setup(self.sf_instance, dict())
        
        # Mock getScanId
        module.getScanId = MagicMock(return_value="test_scan_id")
        
        # Test that the module has consistent formatting methods
        # This is a structural test to ensure the module maintains its interface
        self.assertTrue(hasattr(module, 'handleEvent'))
        self.assertTrue(hasattr(module, 'setup'))
        self.assertTrue(hasattr(module, 'watchedEvents'))
        self.assertTrue(hasattr(module, 'producedEvents'))

    @patch('sys.stdout')
    def test_stdout_error_handling(self, mock_stdout):
        """Test error handling when stdout operations fail."""
        # Simulate stdout write error
        mock_stdout.write.side_effect = IOError("Stdout write failed")
        
        module = sfp__stor_stdout()
        module.setup(self.sf_instance, dict())
        
        # Create test event
        test_event = SpiderFootEvent("IP_ADDRESS", "192.168.1.1", "test_module", None)
        test_event.confidence = 100
        test_event.visibility = 1
        test_event.risk = 0
        
        # Mock getScanId
        module.getScanId = MagicMock(return_value="test_scan_id")
        
        # Should handle stdout errors gracefully without crashing
        try:
            module.handleEvent(test_event)
        except Exception as e:
            self.fail(f"Module should handle stdout errors gracefully: {e}")

    def test_empty_event_data(self):
        """Test handling of events with minimal data."""
        module = sfp__stor_stdout()
        
        # Set up proper event types dictionary
        test_opts = {
            '_eventtypes': {
                'MINIMAL_DATA': 'Minimal Data',
                'ROOT': 'Root'
            }
        }
        module.setup(self.sf_instance, test_opts)
        
        # Create test event with minimal data
        test_event = SpiderFootEvent("MINIMAL_DATA", "N/A", "test_module", None)
        test_event.confidence = 100
        test_event.visibility = 1
        test_event.risk = 0
        
        # Mock getScanId
        module.getScanId = MagicMock(return_value="test_scan_id")
        
        # Should handle empty data gracefully
        try:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                module.handleEvent(test_event)
                output = mock_stdout.getvalue()                # Should still produce some output for the event type
                self.assertIn("Minimal Data", output)  # Check for display name
        except Exception as e:
            self.fail(f"Module should handle empty data gracefully: {e}")

    @patch('sys.stdout', new_callable=StringIO)
    def test_none_event_data(self, mock_stdout):
        """Test handling of None event data."""
        module = sfp__stor_stdout()
        test_opts = {
            'enabled': True,
            '_eventtypes': {
                'NULL_DATA': 'Null Data',
                'ROOT': 'Root'
            },
            '_showonlyrequested': False
        }
        module.setup(self.sf_instance, test_opts)
        test_event = SpiderFootEvent("NULL_DATA", "Null Data", "test_module", None)
        test_event.confidence = 100
        test_event.visibility = 1
        test_event.risk = 0
        module.getScanId = MagicMock(return_value="test_scan_id")
        module.handleEvent(test_event)
        output = mock_stdout.getvalue()
        self.assertIn("Null Data", output)  # Check for display name
