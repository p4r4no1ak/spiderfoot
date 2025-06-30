import pytest
import unittest

from modules.sfp_crt import sfp_crt
from spiderfoot.sflib import SpiderFoot
from test.unit.utils.test_base import SpiderFootTestBase
from test.unit.utils.test_helpers import safe_recursion


class TestModuleCrt(SpiderFootTestBase):

    def test_opts(self):
        module = sfp_crt()
        self.assertEqual(len(module.opts), len(module.optdescs))

    def test_setup(self):
        sf = SpiderFoot(self.default_options)
        module = sfp_crt()
        module.setup(sf, dict())

    def test_watchedEvents_should_return_list(self):
        module = sfp_crt()
        self.assertIsInstance(module.watchedEvents(), list)

    def test_producedEvents_should_return_list(self):
        module = sfp_crt()
        self.assertIsInstance(module.producedEvents(), list)

    def test_parseApiResponse_nonfatal_http_response_code_should_not_set_errorState(self):
        sf = SpiderFoot(self.default_options)

        http_codes = ["200", "404"]
        for code in http_codes:
            with self.subTest(code=code):
                module = sfp_crt()
                module.setup(sf, dict())
                result = module.parseApiResponse(
                    {"code": code, "content": None})
                self.assertIsNone(result)
                self.assertFalse(module.errorState)

    def test_parseApiResponse_fatal_http_response_error_code_should_set_errorState(self):
        sf = SpiderFoot(self.default_options)

        http_codes = ["401", "403", "429", "500", "502", "503"]
        for code in http_codes:
            with self.subTest(code=code):
                module = sfp_crt()
                module.setup(sf, dict())
                result = module.parseApiResponse(
                    {"code": code, "content": None})
                self.assertIsNone(result)
                self.assertTrue(module.errorState)

    def setUp(self):
        """Set up before each test."""
        super().setUp()
        # Register event emitters if they exist
        if hasattr(self, 'module'):
            self.register_event_emitter(self.module)

    def tearDown(self):
        """Clean up after each test."""
        super().tearDown()
