"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import unittest2

from uuid import uuid4
from cafe.drivers.unittest.decorators import tags
from cloudroast.meniscus.fixtures import StatusFixture


class CoordinatorAPI(StatusFixture):

    def set_check_worker(self, hostname=None, ip_v4=None, ip_v6=None,
                         personality=None, status=None, os_type=None):
        orig_resp = self.pairing_behaviors.pair_worker_from_config(
            hostname=hostname, ip_v4=ip_v4, ip_v6=ip_v6,
            personality=personality, status=status, os_type=os_type)
        self.assertEqual(orig_resp.status_code, 202)

        worker_id = orig_resp.entity.worker_id

        resp = self.status_client.get_worker_status(worker_id=worker_id)
        self.assertEqual(resp.status_code, 200)

        if hostname:
            self.assertEqual(resp.entity.hostname, hostname)
        if ip_v4:
            self.assertEqual(resp.entity.ip_v4, ip_v4)
        if ip_v6:
            self.assertEqual(resp.entity.ip_v6, ip_v6)
        if personality:
            self.assertEqual(resp.entity.personality, personality)
        if status:
            self.assertEqual(resp.entity.status, status)
        if os_type:
            self.assertEqual(resp.entity.system_info.os_type, os_type)

    @tags(type='positive')
    def test_hostname_number_string(self):
        self.set_check_worker(hostname='1234')

    @tags(type='positive')
    def test_hostname_uuid(self):
        self.set_check_worker(hostname=str(uuid4()))

    @tags(type='positive')
    def test_hostname_255_len(self):
        hostname = ''
        for _ in range(0, 255):
            hostname += 'a'
        self.set_check_worker(hostname=hostname)

    @tags(type='positive')
    def test_hostname_fqdn(self):
        self.set_check_worker(hostname='rackspace.com')

    @tags(type='positive')
    def test_hostname_subdomain(self):
        self.set_check_worker(hostname='www.rackspace.com')

    @tags(type='positive')
    def test_hostname_http_scheme(self):
        self.set_check_worker(hostname='http://www.rackspace.com')

    @tags(type='positive')
    def test_ipv4_zeros(self):
        self.set_check_worker(ip_v4='0.0.0.0')

    @tags(type='positive')
    def test_ipv4_max(self):
        self.set_check_worker(ip_v4='255.255.255.255')

    @tags(type='positive')
    def test_ipv6_zeros(self):
        address = '0000:0000:0000:0000:0000:0000:0000:0000'
        self.set_check_worker(ip_v6=address)

    @tags(type='positive')
    def test_ipv6_max(self):
        address = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        self.set_check_worker(ip_v6=address)

    @tags(type='positive')
    def test_ipv6_combine_zero_sections(self):
        address = 'ffff:fff::ffff:ff:ffff'
        self.set_check_worker(ip_v6=address)

    @tags(type='positive')
    def test_ipv6_combine_all_leading_groups(self):
        address = '::1'
        self.set_check_worker(ip_v6=address)

    @tags(type='positive')
    def test_ipv6_combine_leading_zeros(self):
        address = 'ffff:fff:0:0:0:ffff:ff:ffff'
        self.set_check_worker(ip_v6=address)

    @unittest2.skip('Not implemented in product yet')
    @tags(type='positive')
    def test_personality_correlation(self):
        self.set_check_worker(personality='correlation')

    @unittest2.skip('Not implemented in product yet')
    @tags(type='positive')
    def test_personality_normalization(self):
        self.set_check_worker(personality='normalization')

    @unittest2.skip('Not implemented in product yet')
    @tags(type='positive')
    def test_personality_storage(self):
        self.set_check_worker(personality='storage')

    @tags(type='positive')
    def test_status_new(self):
        self.set_check_worker(status='new')

    @unittest2.skip('Failing for the moment')
    @tags(type='positive')
    def test_status_online(self):
        self.set_check_worker(status='online')

    @unittest2.skip('Failing for the moment')
    @tags(type='positive')
    def test_status_offline(self):
        self.set_check_worker(status='offline')

    @unittest2.skip('Failing for the moment')
    @tags(type='positive')
    def test_status_draining(self):
        self.set_check_worker(status='draining')

    def test_os_len_255(self):
        os_type = ''
        for _ in range(0, 255):
            os_type += 'a'
        self.set_check_worker(hostname=os_type)

    def test_os_alphanumeric(self):
        os_type = 'abcdefghijklmnopqrstuvwxyz'
        os_type += os_type.upper()
        os_type += '0123456789'
        self.set_check_worker(os_type=os_type)

    def test_os_misc_chars(self):
        os_type = '?;:`~!@#$%^&*+-=_()[]{}<>|/\\\'\"'
        self.set_check_worker(os_type=os_type)
