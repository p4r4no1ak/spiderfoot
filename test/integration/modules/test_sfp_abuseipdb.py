import unittest
from test.unit.utils.test_module_base import TestModuleBase
from unittest.mock import patch
import requests
import time

from spiderfoot import SpiderFootEvent, SpiderFootTarget
from modules.sfp_abuseipdb import sfp_abuseipdb
from spiderfoot.sflib import SpiderFoot


class BaseTestModuleIntegration(TestModuleBase):

    def setUp(self):
        self.default_options = {
            '_fetchtimeout': 15,
            '_useragent': 'SpiderFoot',
            '_internettlds': 'com,net,org,info,biz,us,uk',
            '_genericusers': 'admin,administrator,webmaster,hostmaster,postmaster,root,abuse',
        }
        self.sf = SpiderFoot(self.default_options)
        self.module = self.module_class()
        # Set a dummy API key and required options for testing
        opts = dict(self.default_options)
        opts['api_key'] = 'DUMMY_KEY'
        self.module.setup(self.sf, opts)
        # Set __name__ attribute for event emission
        self.module.__name__ = "sfp_abuseipdb"

    def requests_get_with_retries(self, url, timeout, retries=3, backoff_factor=0.3):
        for i in range(retries):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if i < retries - 1:
                    time.sleep(backoff_factor * (2 ** i))
                else:
                    raise e

    def create_event(self, target_value, target_type, event_type, event_data=None):
        # Ensure event_data is not empty
        if not event_data:
            event_data = 'dummy_data'
        target = SpiderFootTarget(target_value, target_type)
        evt = SpiderFootEvent(event_type, event_data, 'testModule', None)
        return target, evt


class TestModuleIntegrationAbuseIPDB(BaseTestModuleIntegration):

    module_class = sfp_abuseipdb

    @patch('modules.sfp_abuseipdb.requests.get')
    def test_handleEvent_malicious_ip(self, mock_get):
        # Patch fetchUrl to return a blacklist containing the test IP
        import unittest.mock as mock_mod
        blacklist_content = '1.2.3.4\n'
        fetch_url_response = {'code': '200', 'content': blacklist_content}
        with mock_mod.patch.object(self.sf, 'fetchUrl', return_value=fetch_url_response):
            target_value = '1.2.3.4'
            target_type = 'IP_ADDRESS'
            target, evt = self.create_event(target_value, target_type, 'IP_ADDRESS', '1.2.3.4')
            self.module.setTarget(target)
            events = []
            def collect_event(evt):
                events.append(evt)
            with mock_mod.patch.object(self.module, 'notifyListeners', side_effect=collect_event):
                self.module.handleEvent(evt)
            self.assertTrue(any(e.eventType == 'MALICIOUS_IPADDR' for e in events))
            self.assertTrue(any(e.eventType == 'BLACKLISTED_IPADDR' for e in events))
            malicious_ip_event = next((e for e in events if e.eventType == 'MALICIOUS_IPADDR'), None)
            self.assertIsNotNone(malicious_ip_event)
            self.assertIn('AbuseIPDB', malicious_ip_event.data)
            blacklist_event = next((e for e in events if e.eventType == 'BLACKLISTED_IPADDR'), None)
            self.assertIsNotNone(blacklist_event)
            self.assertIn('AbuseIPDB', blacklist_event.data)
