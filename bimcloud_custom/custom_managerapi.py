from bimcloud_api.managerapi import ManagerApi
from bimcloud_api.url import join_url
import requests


class CustomManagerApi(ManagerApi):
    def __init__(self, manager_url):
        super().__init__(manager_url)

    def get_projects(self, auth_context):
        url = join_url(self._api_root, 'get-projects')
        result = self.refresh_on_expiration(requests.get, auth_context, url)
        return result

    def get_libraries(self, auth_context):
        url = join_url(self._api_root, 'get-libraries')
        result = self.refresh_on_expiration(requests.get, auth_context, url)
        return result

    def create_resource_backup(self, auth_context, resource_id, backup_type, name):
        url = join_url(self._api_root, 'create-resource-backup')
        result = self.refresh_on_expiration(requests.post, auth_context, url,
                                            params={'resource-id': resource_id, 'backup-type': backup_type,
                                                    'backup-name': name}, json={})
        return result

    def get_backups(self, auth_context):
        url = join_url(self._api_root, 'get-backups')
        result = self.refresh_on_expiration(requests.get, auth_context, url, params={}, json={})
        return result

    def get_resource_backups_by_criterion(self, auth_context, resourcesIds, filters={}, criterion={}):
        url = join_url(self._api_root, 'get-resource-backups-by-criterion')
        result = self.refresh_on_expiration(requests.post, auth_context, url, params={},
                                            json={'ids': resourcesIds, **filters, **criterion})
        return result

    def delete_resource_backup(self, auth_context, resource_id, backup_id):
        url = join_url(self._api_root, 'delete-resource-backup')
        result = self.refresh_on_expiration(requests.delete, auth_context, url,
                                            params={'resource-id': resource_id, 'backup-id': backup_id}, json={})
        return result
