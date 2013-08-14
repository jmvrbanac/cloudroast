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
import unittest
from json import dumps as dict_to_str
from cafe.drivers.unittest.decorators import tags
from cloudroast.meniscus.fixtures import StatusFixture


class TestStatus(StatusFixture):

    def setUp(self):
        super(TestStatus, self).setUp()
        self.pairing_resp = self.pairing_behaviors.pair_worker_from_config()
        self.assertEqual(self.pairing_resp.status_code, 202)
        self.pairing_info = self.pairing_resp.entity

    def set_and_check_load_average(self, one=None, five=None, fifteen=None,
                                   success=True):
        worker_id = self.pairing_info.worker_id
        worker_token = self.pairing_info.worker_token
        resp = self.status_behaviors.update_load_average(
            worker_id=worker_id,
            worker_token=worker_token,
            one=one,
            five=five,
            fifteen=fifteen)
        if success:
            self.assertEqual(resp.status_code, 200)

            resp = self.status_client.get_worker_status(worker_id)
            self.assertEqual(resp.status_code, 200)
            self.assertIsNotNone(resp.entity)
            self.assertIsNotNone(resp.entity.system_info)

            load_average = resp.entity.system_info.load_average
            self.assertEqual(load_average.one_average, one)
            self.assertEqual(load_average.five_average, five)
            self.assertEqual(load_average.fifteen_average, fifteen)
        else:
            self.assertEqual(resp.status_code, 400)

    def set_and_check_disk_usage(self, device, total, used, success=True):
        worker_id = self.pairing_info.worker_id
        worker_token = self.pairing_info.worker_token
        disks = [{'device': device, 'total': total, 'used': used }]

        resp = self.status_behaviors.update_status_from_config(
            worker_id=worker_id,
            worker_token=worker_token,
            disks=disks)

        if success:
            self.assertEqual(resp.status_code, 200)
        else:
            self.assertEqual(resp.status_code, 400)



    @tags(type='positive')
    def test_set_load_to_zero(self):
        self.set_and_check_load_average(one=0, five=0, fifteen=0)

    @tags(type='positive')
    def test_set_load_to_float(self):
        self.set_and_check_load_average(one=0.1, five=0.1, fifteen=0.1)

    @tags(type='negative')
    @unittest.skip('GitHub #327')
    def test_set_load_to_neg_numbers(self):
        self.set_and_check_load_average(one=-2,
                                        five=-2,
                                        fifteen=-2,
                                        success=False)

    @tags(type='negative')
    def test_set_load_to_empty_strings(self):
        self.set_and_check_load_average(one='',
                                        five='',
                                        fifteen='',
                                        success=False)
    @tags(type='negative')
    def test_set_load_to_nulls(self):
        self.set_and_check_load_average(one=None,
                                        five=None,
                                        fifteen=None,
                                        success=False)

    @tags(type='negative')
    def test_set_load_with_invalid_body(self):
        worker_id = self.pairing_info.worker_id
        worker_token = self.pairing_info.worker_token
        data = dict_to_str({"load_average": "didn't validate me"})

        resp = self.status_client.direct_update(worker_id=worker_id,
                                                worker_token=worker_token,
                                                body=data)
        self.assertEqual(resp.status_code, 400)

    @tags(type='positive')
    def test_set_usage_values_ints(self):
        self.set_and_check_disk_usage(device='/dev/sda1',
                                      total=10000,
                                      used=5000)

    @tags(type='positive')
    def test_set_usage_sys_path(self):
        self.set_and_check_disk_usage(device='/sys/devices/blk1',
                                      total=10000,
                                      used=5000)

    @tags(type='negative')
    def test_set_usage_values_num_strings(self):
        self.set_and_check_disk_usage(device='/dev/sda1',
                                      total='10000',
                                      used='5000',
                                      success=False)

    @tags(type='negative')
    def test_set_usage_values_invalid_strings(self):
        self.set_and_check_disk_usage(device='boom',
                                      total='trace',
                                      used='boom',
                                      success=False)

    @tags(type='negative')
    def test_set_usage_with_invalid_body(self):
        worker_id = self.pairing_info.worker_id
        worker_token = self.pairing_info.worker_token
        data = dict_to_str({'disk_usage': 'random_str'})

        resp = self.status_client.direct_update(worker_id=worker_id,
                                                worker_token=worker_token,
                                                body=data)
        self.assertEqual(resp.status_code, 400)