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
from test_repo.meniscus.fixtures import PublishingFixture


class PublishingAPI(PublishingFixture):

    @unittest2.skip('GitHub #238')
    def test_publishing_wout_valid_host(self):
        """ Verifies that invalid given host returns a 400
        - Reported in GitHub Meniscus Issue #238
        """
        resp = self.publish_behaviors.publish_overriding_config(host='bad')
        self.assertEqual(resp.status_code, 400)
