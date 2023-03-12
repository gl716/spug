# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <spug.dev@gmail.com>
# Released under the AGPL-3.0 License.
from django.urls import path

from apps.apis import config
from apps.apis import deploy
from apps.apis import importData

urlpatterns = [
    path('config/', config.get_configs),
    path('deploy/<int:deploy_id>/<str:kind>/', deploy.auto_deploy),
    path('import/', importData.import_app),

]
