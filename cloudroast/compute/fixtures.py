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

import sys

from cloudcafe.blockstorage.v1.volumes_api.client import VolumesClient
from cloudcafe.blockstorage.v1.config import BlockStorageConfig
from cloudcafe.blockstorage.v1.volumes_api.behaviors import \
    VolumesAPI_Behaviors
from cloudcafe.blockstorage.v1.volumes_api.config import VolumesAPIConfig
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.common.resources import ResourcePool
from cloudcafe.compute.config import ComputeEndpointConfig, \
    ComputeAdminEndpointConfig, MarshallingConfig, ComputeFuzzingConfig
from cloudcafe.compute.common.exception_handler import ExceptionHandler
from cloudcafe.compute.extensions.vnc_console_api.client\
    import VncConsoleClient
from cloudcafe.compute.extensions.console_output_api.client\
    import ConsoleOutputClient
from cloudcafe.compute.flavors_api.client import FlavorsClient
from cloudcafe.compute.quotas_api.client import QuotasClient
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.compute.images_api.client import ImagesClient
from cloudcafe.compute.hosts_api.client import HostsClient
from cloudcafe.compute.hypervisors_api.client import HypervisorsClient
from cloudcafe.compute.extensions.keypairs_api.client import KeypairsClient
from cloudcafe.compute.extensions.security_groups_api.client import \
    SecurityGroupsClient, SecurityGroupRulesClient
from cloudcafe.compute.extensions.rescue_api.client import RescueClient
from cloudcafe.compute.limits_api.client import LimitsClient
from cloudcafe.compute.extensions.config_drive.behaviors import \
    ConfigDriveBehaviors
from cloudcafe.compute.extensions.config_drive.config import ConfigDriveConfig
from cloudcafe.compute.extensions.config_drive.config import CloudInitConfig
from cloudcafe.compute.servers_api.behaviors import ServerBehaviors
from cloudcafe.compute.images_api.behaviors import ImageBehaviors
from cloudcafe.auth.config import UserAuthConfig, UserConfig, \
    ComputeAdminAuthConfig, ComputeAdminUserConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudcafe.compute.images_api.config import ImagesConfig
from cloudcafe.compute.servers_api.config import ServersConfig
from cloudcafe.compute.volume_attachments_api.volume_attachments_client \
    import VolumeAttachmentsAPIClient


class ComputeFixture(BaseTestFixture):
    """
    @summary: Base fixture for compute tests
    """

    @classmethod
    def setUpClass(cls):
        super(ComputeFixture, cls).setUpClass()
        cls.flavors_config = FlavorsConfig()
        cls.images_config = ImagesConfig()
        cls.servers_config = ServersConfig()
        cls.compute_endpoint = ComputeEndpointConfig()
        cls.marshalling = MarshallingConfig()
        cls.config_drive_config = ConfigDriveConfig()
        cls.cloud_init_config = CloudInitConfig()

        cls.flavor_ref = cls.flavors_config.primary_flavor
        cls.flavor_ref_alt = cls.flavors_config.secondary_flavor
        cls.image_ref = cls.images_config.primary_image
        cls.image_ref_alt = cls.images_config.secondary_image
        cls.disk_path = cls.servers_config.instance_disk_path
        cls.split_ephemeral_disk_enabled = \
            cls.servers_config.split_ephemeral_disk_enabled
        cls.ephemeral_disk_max_size = \
            cls.servers_config.ephemeral_disk_max_size
        cls.disk_format_type = cls.servers_config.disk_format_type

        cls.endpoint_config = UserAuthConfig()
        cls.user_config = UserConfig()
        cls.access_data = AuthProvider.get_access_data(cls.endpoint_config,
                                                       cls.user_config)
        # If authentication fails, halt
        if cls.access_data is None:
            cls.assertClassSetupFailure('Authentication failed.')

        compute_service = cls.access_data.get_service(
            cls.compute_endpoint.compute_endpoint_name)
        url = compute_service.get_endpoint(
            cls.compute_endpoint.region).public_url
        # If a url override was provided, use that value instead
        if cls.compute_endpoint.compute_endpoint_url:
            url = '{0}/{1}'.format(cls.compute_endpoint.compute_endpoint_url,
                                   cls.user_config.tenant_id)

        client_args = {'url': url, 'auth_token': cls.access_data.token.id_,
                       'serialize_format': cls.marshalling.serializer,
                       'deserialize_format': cls.marshalling.deserializer}

        cls.flavors_client = FlavorsClient(**client_args)
        cls.servers_client = ServersClient(**client_args)
        cls.images_client = ImagesClient(**client_args)
        cls.keypairs_client = KeypairsClient(**client_args)
        cls.security_groups_client = SecurityGroupsClient(**client_args)
        cls.security_group_rule_client = SecurityGroupRulesClient(
            **client_args)
        cls.volume_attachments_client = VolumeAttachmentsAPIClient(
            url=url, auth_token=cls.access_data.token.id_,
            tenant_id=cls.user_config.tenant_id,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.rescue_client = RescueClient(**client_args)
        cls.vnc_client = VncConsoleClient(**client_args)
        cls.console_output_client = ConsoleOutputClient(**client_args)
        cls.limits_client = LimitsClient(**client_args)
        cls.server_behaviors = ServerBehaviors(cls.servers_client,
                                               cls.servers_config,
                                               cls.images_config,
                                               cls.flavors_config)
        cls.image_behaviors = ImageBehaviors(cls.images_client,
                                             cls.servers_client,
                                             cls.images_config)
        cls.config_drive_behaviors = ConfigDriveBehaviors(cls.servers_client,
                                                          cls.servers_config,
                                                          cls.server_behaviors)
        cls.flavors_client.add_exception_handler(ExceptionHandler())
        cls.resources = ResourcePool()

    @classmethod
    def tearDownClass(cls):
        super(ComputeFixture, cls).tearDownClass()
        cls.flavors_client.delete_exception_handler(ExceptionHandler())
        cls.resources.release()

    @classmethod
    def parse_image_id(cls, image_response):
        """
        @summary: Extract Image Id from Image response
        @param image_response: Image response
        @type image_response: string
        @return: Image id
        @rtype: string
        """
        image_ref = image_response.headers['location']
        return image_ref.rsplit('/')[-1]

    def validate_instance_action(self, action, server_id,
                                 user_id, project_id, request_id):
        message = "Expected {0} to be {1}, was {2}."

        self.assertEqual(action.instance_uuid, server_id,
                         msg=message.format('instance id',
                                            action.instance_uuid,
                                            server_id))
        self.assertEqual(action.user_id, user_id,
                         msg=message.format('user id',
                                            action.user_id,
                                            user_id))
        self.assertEqual(action.project_id, project_id,
                         msg=message.format('project id',
                                            action.project_id,
                                            project_id))
        self.assertIsNotNone(action.start_time)
        self.assertEquals(action.request_id, request_id,
                          msg=message.format('request id',
                                             action.request_id,
                                             request_id))
        self.assertIsNone(action.message)

    def _verify_ephemeral_disk_size(self, disks, flavor,
                                    split_ephemeral_disk_enabled=False,
                                    ephemeral_disk_max_size=sys.maxint):

        ephemeral_disk_size = flavor.ephemeral_disk

        # If ephemeral disk splitting is enabled, determine the number of
        # ephemeral disks that should be present
        if split_ephemeral_disk_enabled:
            instance_ephemeral_disks = len(disks.keys())
            self.assertEqual(
                instance_ephemeral_disks,
                int(flavor.extra_specs.get('number_of_data_disks')))

            # If the ephemeral disk size exceeds the max size,
            # set the ephemeral_disk_size to the maximum ephemeral disk size
            ephemeral_disk_size = min(ephemeral_disk_max_size,
                                      ephemeral_disk_size)

        # Validate the size of each disk
        for disk, size in disks.iteritems():
            self.assertEqual(size, ephemeral_disk_size)

    def _format_disk(self, remote_client, disk, disk_format):
        remote_client.format_disk(filesystem_type=disk_format, disk=disk)

    def _mount_disk(self, remote_client, disk, mount_point):
        remote_client.create_directory(mount_point)
        remote_client.mount_disk(disk, mount_point)


class ComputeAdminFixture(ComputeFixture):
    """
    @summary: Base fixture for compute tests
    """

    @classmethod
    def setUpClass(cls):
        super(ComputeAdminFixture, cls).setUpClass()

        # Setup admin client
        auth_config = ComputeAdminAuthConfig()
        user_config = ComputeAdminUserConfig()
        access_data = AuthProvider.get_access_data(auth_config,
                                                   user_config)
        admin_endpoint_config = ComputeAdminEndpointConfig()
        compute_service = access_data.get_service(
            admin_endpoint_config.compute_endpoint_name)
        url = compute_service.get_endpoint(
            admin_endpoint_config.region).public_url

        client_args = {'url': url, 'auth_token': access_data.token.id_,
                       'serialize_format': cls.marshalling.serializer,
                       'deserialize_format': cls.marshalling.deserializer}

        cls.admin_flavors_client = FlavorsClient(**client_args)
        cls.admin_servers_client = ServersClient(**client_args)
        cls.admin_images_client = ImagesClient(**client_args)
        cls.admin_hosts_client = HostsClient(**client_args)
        cls.admin_quotas_client = QuotasClient(**client_args)
        cls.admin_hypervisors_client = HypervisorsClient(**client_args)
        cls.admin_server_behaviors = ServerBehaviors(cls.admin_servers_client,
                                                     cls.servers_config,
                                                     cls.images_config,
                                                     cls.flavors_config)
        cls.admin_images_behaviors = ImageBehaviors(cls.admin_images_client,
                                                    cls.admin_servers_client,
                                                    cls.images_config)
        cls.admin_servers_client.add_exception_handler(ExceptionHandler())

    @classmethod
    def tearDownClass(cls):
        super(ComputeAdminFixture, cls).tearDownClass()
        cls.flavors_client.delete_exception_handler(ExceptionHandler())
        cls.resources.release()


class BlockstorageIntegrationFixture(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(BlockstorageIntegrationFixture, cls).setUpClass()

        block_config = BlockStorageConfig()
        volumes_config = VolumesAPIConfig()
        cls.poll_frequency = volumes_config.volume_status_poll_frequency
        cls.volume_status_timeout = volumes_config.volume_create_max_timeout
        cls.volume_size = int(volumes_config.min_volume_size)
        cls.volume_type = volumes_config.default_volume_type

        block_service = cls.access_data.get_service(
            block_config.identity_service_name)
        block_url = block_service.get_endpoint(
            block_config.region).public_url
        cls.storage_client = VolumesClient(
            block_url, cls.access_data.token.id_,
            cls.marshalling.serializer, cls.marshalling.deserializer)
        cls.storage_behavior = VolumesAPI_Behaviors(
            volumes_api_client=cls.storage_client,
            volumes_api_config=volumes_config)


class FlavorIdNegativeDataList(DatasetList):
    def __init__(self):
        super(FlavorIdNegativeDataList, self).__init__()
        fuzz_config = ComputeFuzzingConfig()
        with open(fuzz_config.input_fuzzing_file) as f:
            for line in f:
                self.append_new_dataset(line, {'flavor_id': line})


class ImageIdNegativeDataList(DatasetList):
    def __init__(self):
        super(ImageIdNegativeDataList, self).__init__()
        fuzz_config = ComputeFuzzingConfig()
        with open(fuzz_config.input_fuzzing_file) as f:
            for line in f:
                self.append_new_dataset(line, {'image_id': line})


class ServerIdNegativeDataList(DatasetList):
    def __init__(self):
        super(ServerIdNegativeDataList, self).__init__()
        fuzz_config = ComputeFuzzingConfig()
        with open(fuzz_config.input_fuzzing_file) as f:
            for line in f:
                self.append_new_dataset(line, {'server_id': line})
