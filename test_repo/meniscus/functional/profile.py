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
from cloudcafe.compute.common.datagen import random_int
from test_repo.meniscus.fixtures import ProfileFixture


class TenantAPIProfile(ProfileFixture):

    @tags(type='positive')
    def test_create_profile_with_only_required(self):
        """
        Only the name is required to create a profile
        """
        profile_name = self.tenant_config.profile_name
        resp = self.profile_behaviors.create_profile(name=profile_name)

        # Should be covered in behavior, but just in case
        self.assertEqual(resp['request'].status_code, 201)

    @tags(type='positive')
    def test_create_profile_with_name_uuid(self):
        """
        Should be able to create a profile with a uuid for the name
        """
        profile_name = str(uuid4())
        resp = self.profile_behaviors.create_profile(name=profile_name)

        # Should be covered in behavior, but just in case
        self.assertEqual(resp['request'].status_code, 201)

    @tags(type='negative')
    def test_create_profile_with_int_name(self):
        """
        Shouldn't be able to create a profile with the name being an int
        """
        profile_name = random_int(0, 100000)
        resp = self.profile_behaviors.create_profile(name=profile_name)
        self.assertEqual(resp['request'].status_code, 400)

    @tags(type='negative')
    def test_create_profile_with_bogus_producer_id(self):
        """
        Should return an error when you pass in a bogus producer id.
        - Reported in GitHub #272
        """
        profile_name = str(random_int(0, 100000))
        producer_ids = [9999999999]
        resp = self.profile_behaviors.create_profile(name=profile_name,
                                                     producer_ids=producer_ids)
        self.assertEqual(resp['request'].status_code, 400)

    @tags(type='positive')
    def test_update_profile_with_uuid_name(self):
        """
        Should be able to create a profile with a uuid for the name
        """
        profile_name = str(uuid4())
        resp = self.profile_behaviors.create_profile_from_cfg()
        self.assertEqual(resp['request'].status_code, 201)

        resp = self.profile_client.update_profile(
            id=resp['profile_id'],
            name=profile_name)

        self.assertEqual(resp.status_code, 200)