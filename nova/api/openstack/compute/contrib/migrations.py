# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api.openstack import xmlutil
from nova import compute


XMLNS = "http://docs.openstack.org/compute/ext/migrations/api/v2.0"
ALIAS = "os-migrations"


def authorize(context, action_name):
    action = 'migrations:%s' % action_name
    extensions.extension_authorizer('compute', action)(context)


class MigrationsTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('migrations')
        elem = xmlutil.SubTemplateElement(root, 'migration',
                                          selector='migrations')
        elem.set('id')
        elem.set('source_node')
        elem.set('dest_node')
        elem.set('source_compute')
        elem.set('dest_compute')
        elem.set('dest_host')
        elem.set('status')
        elem.set('instance_uuid')
        elem.set('old_instance_type_id')
        elem.set('new_instance_type_id')
        elem.set('created_at')
        elem.set('updated_at')

        return xmlutil.MasterTemplate(root, 1)


class MigrationsController(object):
    """Controller for accessing migrations in OpenStack API."""
    def __init__(self):
        self.compute_api = compute.API()

    @wsgi.serializers(xml=MigrationsTemplate)
    def index(self, req):
        """Return all migrations in progress."""
        context = req.environ['nova.context']
        authorize(context, "index")
        migrations = self.compute_api.get_migrations(context, req.GET)
        return {'migrations': migrations}


class Migrations(extensions.ExtensionDescriptor):
    """Provide data on migrations."""
    name = "Migrations"
    alias = ALIAS
    namespace = XMLNS
    updated = "2013-05-30T00:00:00+00:00"

    def get_resources(self):
        resources = []
        resource = extensions.ResourceExtension('os-migrations',
                                                MigrationsController())
        resources.append(resource)
        return resources
