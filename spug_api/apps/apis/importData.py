import json

from django.http import HttpResponse, Http404
from apps.account.models import User
from apps.app.models import App, Deploy, DeployExtend1
from apps.config.models import Environment


def import_app(request):
    user = User.objects.get(id=1)
    if request.method == 'POST':
        data = json.loads(request.body)
        env_map = {'1': 'dev', '2': 'test', '3': 'uat', '4': 'prod'}
        print(data['apps'])
        for t in data['apps']:
            environments = Environment.objects.filter(id=t[2]).all()
            if not environments:
                print(f'环境不存在：{t[2]}')
                raise Http404
            apps = App.objects.filter(key=t[1]).all()
            app = App()
            if apps:
                app = apps[0]
            app.created_by = user
            app.name = t[0]
            app.key = t[1]
            app.save()

            deploys = Deploy.objects.filter(app_id=app.id, env_id=t[2]).all()
            deploy = Deploy()
            if deploys:
                deploy = deploys[0]
            deploy.host_ids = f"[{t[3]}]"
            deploy.extend = 1
            deploy.is_audit = 0
            deploy.is_parallel = 0
            deploy.rst_notify = '{"mode":"0"}'
            deploy.app = app
            deploy.created_by = user
            deploy.env = environments[0]
            deploy.save()

            deploy_extend1 = DeployExtend1()
            if deploy.deployextend1:
                deploy_extend1 = deploy.deployextend1
            deploy_extend1.deploy = deploy
            deploy_extend1.git_repo = t[4]
            deploy_extend1.dst_dir = t[5]
            deploy_extend1.dst_repo = '~/release'
            deploy_extend1.versions = 5
            deploy_extend1.filter_rule = '{"type": "contain", "data": "target/*.jar"}'
            deploy_extend1.hook_pre_host = 'rm -rf $SPUG_DST_DIR'
            deploy_extend1.hook_post_server = t[6] if t[6] else f"mvn{env_map[t[2]]} install"
            deploy_extend1.hook_post_host = t[7] if t[
                7] else 'wget http://w.metaitsaas.com/run.sh -o /dev/null\nchmod +x run.sh\n./run.sh -g restart'
            deploy_extend1.save()

    return HttpResponse('OK')
