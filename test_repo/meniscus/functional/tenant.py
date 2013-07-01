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
from test_repo.meniscus.fixtures import TenantFixture


class TenantAPI(TenantFixture):

    @tags(type='positive')
    def test_get_tenant_w_uuid(self):
        """ Verify that we can retrieve tenant with id being a uuid"""
        tenant_id, resp = self.tenant_behaviors.create_tenant(str(uuid4()))
        self.assertEqual(resp.status_code, 201)

        resp = self.tenant_client.get_tenant(tenant_id)
        self.assertEqual(resp.status_code, 200)

    @tags(type='positive')
    def test_get_tenant_w_int(self):
        """ Verify that we can retrieve tenant with id being an int"""
        tenant_id, resp = self.tenant_behaviors.create_tenant()
        self.assertEqual(resp.status_code, 201)

        resp = self.tenant_client.get_tenant(tenant_id)
        self.assertEqual(resp.status_code, 200)

    @tags(type='positive')
    def test_get_tenant_w_long_str(self):
        """ Verify that we can retrieve tenant with id length of 256"""
        tenant_id = ''.join(['a' for _ in range(256)])
        tenant_id, resp = self.tenant_behaviors.create_tenant(tenant_id)
        self.assertEqual(resp.status_code, 201)

        resp = self.tenant_client.get_tenant(tenant_id)
        self.assertEqual(resp.status_code, 200)

    @tags(type='positive')
    @unittest2.skip('GitHub #268')
    def test_reset_tenant_token_now(self):
        """ Verify that we can reset the tenant token"""
        tenant_id, resp = self.tenant_behaviors.create_tenant()
        self.assertEqual(resp.status_code, 201)

        resp = self.tenant_client.get_tenant(tenant_id)
        self.assertEqual(resp.status_code, 200)
        orig_token = resp.entity[0].token

        resp = self.tenant_client.reset_token(tenant_id, invalidate_now=True)
        self.assertEqual(resp.status_code, 203)

        resp = self.tenant_client.get_tenant(tenant_id)
        new_token = resp.entity[0].token

        self.assertNotEqual(new_token, orig_token)

    @tags(type='positive')
    @unittest2.skip('GitHub #268')
    def test_reset_tenant_token_later(self):
        """ Verify that we can reset the tenant token"""
        tenant_id, resp = self.tenant_behaviors.create_tenant()
        self.assertEqual(resp.status_code, 201)

        resp = self.tenant_client.get_tenant(tenant_id)
        self.assertEqual(resp.status_code, 200)
        orig_token = resp.entity[0].token

        resp = self.tenant_client.reset_token(tenant_id, invalidate_now=False)
        self.assertEqual(resp.status_code, 203)

        resp = self.tenant_client.get_tenant(tenant_id)
        new_token = resp.entity[0].token

        self.assertNotEqual(new_token, orig_token)
        self.assertEqual(new_token.previous, orig_token.valid)
