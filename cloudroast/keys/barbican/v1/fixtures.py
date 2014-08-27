import json
import requests
from specter import Spec, fixture

from cloudcafe.cloudkeep.config import MarshallingConfig
from cloudcafe.cloudkeep.config import CloudKeepConfig
from cloudcafe.cloudkeep.config import CloudKeepAuthConfig

from cloudcafe.keys.barbican.clients.version import VersionClient

# from cloudcafe.cloudkeep.config import CloudKeepSecretsConfig
# from cloudcafe.cloudkeep.config import CloudKeepOrdersConfig


@fixture
class BarbicanFixture(Spec):
    def before_all(self, keystone_config=None):
        self.marshalling = MarshallingConfig()
        self.cloudkeep = CloudKeepConfig()
        self.keystone = keystone_config or CloudKeepAuthConfig()

        self.token, self.tenant_id = self._get_token_and_id(
            endpoint=self.keystone.authentication_endpoint,
            username=self.keystone.username,
            password=self.keystone.password,
            tenant=self.keystone.tenant_name,
            auth_type=self.keystone.auth_type)

        self.version_client = VersionClient(
            url=self.cloudkeep.base_url,
            token=self.token,
            serialize_format=self.marshalling.serializer,
            deserialize_format=self.marshalling.deserializer)

    def _get_token_and_id(self, endpoint, username, password,
                          tenant, auth_type='keystone'):
        """ This is temporary hack for Keystone and Rackspace Auth. This
        is needed as the Rackspace identity provider does not allow for
        password auth. Currently, I do not have the time to refactor the
        identity provider to handle this.
        THIS IS A HACK! DO NOT DUPLICATE THIS!

        TODO: Refactor Identity rackspace auth provider to handle passwords
              and multiple roles.
        """
        # Build request data
        endpoint = '{base}/v2.0/tokens'.format(base=endpoint)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # All strict Keystone implementations should use 'tenantName'
        auth_key = 'tenantId' if auth_type == 'rackspace' else 'tenantName'
        auth = json.dumps({
            'auth': {
                'passwordCredentials': {
                    'username': username,
                    'password': password
                },
                auth_key: tenant
            }
        })

        # Make request
        resp = requests.post(endpoint, data=auth, headers=headers)
        resp_dict = json.loads(resp.content)
        if not resp.ok:
            raise Exception('Failed to authenticate! {0}'.format(resp.content))

        # Get dictionaries from response (default to empty)
        access_dict = resp_dict.get('access', {})
        token_dict = access_dict.get('token', {})
        tenant_dict = token_dict.get('tenant', {})

        token_id = token_dict.get('id')
        tenant_id = tenant_dict.get('id')

        return token_id, tenant_id

    def _build_editable_keystone_config(cls):
        loaded_config = CloudKeepAuthConfig()
        # This is far from ideal, but I need to be able to edit the config
        config = type('SpoofedConfig', (object,), {
            'version': loaded_config.version,
            'username': loaded_config.username,
            'password': loaded_config.password,
            'tenant_name': loaded_config.tenant_name,
            'authentication_endpoint': loaded_config.authentication_endpoint,
            'auth_type': loaded_config.auth_type})
        return config
