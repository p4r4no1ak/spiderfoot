import pytest
import unittest
from test.unit.utils.test_module_base import TestModuleBase
from unittest.mock import MagicMock, patch

from modules.sfp__stor_stdout import sfp__stor_stdout
from spiderfoot.sflib import SpiderFoot
from spiderfoot import SpiderFootEvent, SpiderFootTarget


class BaseTestModuleIntegration(TestModuleBase):


    def setUp(self):
        """Enhanced setUp with ThreadReaper module tracking."""
        super().setUp()
        # ThreadReaper infrastructure is automatically initialized
        
    def tearDown(self):
        """Enhanced tearDown with ThreadReaper cleanup."""
        # ThreadReaper infrastructure automatically cleans up
        super().tearDown()
    default_options = {
        'enabled': True,
        '_format': 'tab',
    }

    def setup_module(self, module_class):
        sf = SpiderFoot(self.default_options)
        module = module_class()
        module.setup(sf, dict())
        return module

    def create_event(self, target_value, target_type, event_type, event_data):
        target = SpiderFootTarget(target_value, target_type)
        evt = SpiderFootEvent(event_type, event_data, '', '')
        return target, evt



class TestModuleIntegration_stor_stdout(BaseTestModuleIntegration):


    def setUp(self):
        """Enhanced setUp with ThreadReaper module tracking."""
        super().setUp()
        # ThreadReaper infrastructure is automatically initialized
        
    def tearDown(self):
        """Enhanced tearDown with ThreadReaper cleanup."""
        # ThreadReaper infrastructure automatically cleans up
        super().tearDown()
    def test_handleEvent(self):
        module = self.setup_module(sfp__stor_stdout)

        target_value = 'example target value'
        target_type = 'IP_ADDRESS'
        event_data = 'example data'
        target, evt = self.create_event(
            target_value, target_type, 'ROOT', event_data)

        module.setTarget(target)
        # Patch output to check if called
        with patch.object(module, 'output') as mock_output:
            module.handleEvent(evt)
            # Should not call output for ROOT event
            mock_output.assert_not_called()
        # Now test with a non-ROOT event
        evt2 = SpiderFootEvent('SOME_EVENT', event_data, 'sfp__stor_stdout', None)
        with patch.object(module, 'output') as mock_output:
            module.handleEvent(evt2)
            mock_output.assert_called_once_with(evt2)
