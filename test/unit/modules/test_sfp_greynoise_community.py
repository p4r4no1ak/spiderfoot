# filepath: spiderfoot/test/unit/modules/test_sfp_greynoise_community.py
from unittest.mock import patch, MagicMock
from spiderfoot.sflib import SpiderFoot
from spiderfoot import SpiderFootEvent
from modules.sfp_greynoise_community import sfp_greynoise_community
import unittest
from test.unit.utils.test_module_base import TestModuleBase
from test.unit.utils.test_helpers import safe_recursion


class TestModuleGreynoiseCommunity(TestModuleBase):
    """Test Greynoise Community module."""

    def setUp(self):
        """Set up before each test."""
        super().setUp()
        # Create a mock for any logging calls
        self.log_mock = MagicMock()
        # Apply patches in setup to affect all tests
        patcher1 = patch('logging.getLogger', return_value=self.log_mock)
        self.addCleanup(patcher1.stop)
        self.mock_logger = patcher1.start()

        # Create module wrapper class dynamically
        module_attributes = {
            'descr': "Description for sfp_greynoise_community",
            # Add module-specific options

        }

        self.module_class = self.create_module_wrapper(
            sfp_greynoise_community,
            module_attributes=module_attributes
        )
        # Register event emitters if they exist
        if hasattr(self, 'module'):
            self.register_event_emitter(self.module)
        # Register mocks for cleanup during tearDown
        self.register_mock(self.mock_logger)
        # Register patchers for cleanup during tearDown
        if 'patcher1' in locals():
            self.register_patcher(patcher1)
        self.scanner = sfp_greynoise_community()

    def test_opts(self):
        """Test the module options."""
        module = sfp_greynoise_community()
        self.assertEqual(len(module.opts), len(module.optdescs))

    def test_setup(self):
        """
        Test setup(self, sfc, userOpts=dict())
        """
        sf = SpiderFoot(self.default_options)
        module = sfp_greynoise_community()
        module.setup(sf, dict())
        self.assertIsNotNone(module.opts)
        self.assertTrue('api_key' in module.opts)
        self.assertTrue('age_limit_days' in module.opts)
        self.assertEqual(module.opts['api_key'], "")
        self.assertEqual(module.opts['age_limit_days'], 30)

    def test_watchedEvents_should_return_list(self):
        """Test the watchedEvents function returns a list."""
        module = sfp_greynoise_community()
        self.assertIsInstance(module.watchedEvents(), list)

    def test_producedEvents_should_return_list(self):
        """Test the producedEvents function returns a list."""
        module = sfp_greynoise_community()
        self.assertIsInstance(module.producedEvents(), list)

    def tearDown(self):
        """Clean up after each test."""
        super().tearDown()
