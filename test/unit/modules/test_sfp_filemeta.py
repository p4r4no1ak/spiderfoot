import pytest
import unittest

from modules.sfp_filemeta import sfp_filemeta
from spiderfoot.sflib import SpiderFoot
from test.unit.utils.test_module_base import TestModuleBase
from test.unit.utils.test_helpers import safe_recursion


class TestModuleFilemeta(TestModuleBase):

    def test_opts(self):
        module = sfp_filemeta()
        self.assertEqual(len(module.opts), len(module.optdescs))

    def test_setup(self):
        sf = SpiderFoot(self.default_options)
        module = sfp_filemeta()
        module.setup(sf, dict())

    def test_watchedEvents_should_return_list(self):
        module = sfp_filemeta()
        self.assertIsInstance(module.watchedEvents(), list)

    def test_producedEvents_should_return_list(self):
        module = sfp_filemeta()
        self.assertIsInstance(module.producedEvents(), list)

    def setUp(self):
        """Set up before each test."""
        super().setUp()
        # Register event emitters if they exist
        if hasattr(self, 'module'):
            self.register_event_emitter(self.module)

    def tearDown(self):
        """Clean up after each test."""
        super().tearDown()
