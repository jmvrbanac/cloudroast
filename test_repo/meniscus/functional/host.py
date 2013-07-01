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
from cafe.drivers.unittest.decorators import tags
from test_repo.meniscus.fixtures import HostFixture


class TenantAPIHost(HostFixture):

    def create_and_check_host(self, hostname=None, ip_v4=None, ip_v6=None,
                              profile_id=None):
        """ Doing this until we get parametrized tests """
        hostname = hostname or self.tenant_config.hostname
        args = {
            'hostname': hostname,
            'ip_address_v4': ip_v4,
            'ip_address_v6': ip_v6,
            'profile': profile_id
        }
        resp = self.host_behaviors.create_host(
            hostname=hostname,
            ip_v4=ip_v4,
            ip_v6=ip_v6,
            profile_id=profile_id)
        self.assertEqual(resp['request'].status_code, 201)

        resp = self.host_client.get_host(resp['host_id'])
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.entity)

        for key, value in args.iteritems():
            self.assertEqual(getattr(resp.entity, key), value)

    @tags(type='positive')
    def test_create_host_w_only_required(self):
        self.create_and_check_host()

    @tags(type='positive')
    def test_create_host_w_fqdn(self):
        self.create_and_check_host(hostname='rackspace.com')

    @tags(type='positive')
    def test_create_host_w_subdomain(self):
        self.create_and_check_host(hostname='www.rackspace.com')

    @tags(type='positive')
    def test_create_host_w_scheme(self):
        self.create_and_check_host(hostname='http://www.rackspace.com')

    @tags(type='positive')
    def test_create_host_w_ipv4_zeros(self):
        self.create_and_check_host(ip_v4='0.0.0.0')

    @tags(type='positive')
    def test_create_host_w_ipv4_max(self):
        self.create_and_check_host(ip_v4='255.255.255.255')

    @tags(type='positive')
    def test_create_host_w_ipv6_zeros(self):
        address = '0000:0000:0000:0000:0000:0000:0000:0000'
        self.create_and_check_host(ip_v6=address)

    @tags(type='positive')
    def test_create_host_w_ipv6_max(self):
        address = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        self.create_and_check_host(ip_v6=address)

    @tags(type='positive')
    def test_create_host_w_ipv6_combine_all_leading_zeros(self):
        address = '::1'
        self.create_and_check_host(ip_v6=address)

    @tags(type='positive')
    def test_create_host_w_ipv6_combine_zero_sections(self):
        address = 'ffff:fff::ffff:ff:ffff'
        self.create_and_check_host(ip_v6=address)

    @tags(type='positive')
    def test_create_host_w_ipv6_remove_leading_zeros(self):
        address = 'ffff:fff:0:0:0:ffff:ff:ffff'
        self.create_and_check_host(ip_v6=address)

    @tags(type='positive')
    def test_create_host_w_valid_profile_id(self):
        self.create_and_check_host(profile_id=self.profile_id)

    @tags(type='negative')
    def test_create_host_w_invalid_profile_id(self):
        req = self.host_behaviors.create_host_from_cfg(profile_id=999999)
        self.assertEqual(req['request'].status_code, 400)
