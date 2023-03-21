import json, time

from django.http import HttpResponse, Http404
from apps.account.models import User
from apps.app.models import App, Deploy, DeployExtend1
from apps.host.models import Host
from apps.config.models import Environment


def import_app(request):
    user = User.objects.get(id=1)
    if request.method == 'POST':
        start_time = time.perf_counter()
        data = json.loads(request.body)
        pre_t = None
        all_envs = Environment.objects.all()
        all_hosts = Host.objects.all()
        all_deploys = Deploy.objects.all()
        all_deploy_extend1s = DeployExtend1.objects.all()
        apps = data['apps']
        print(type(apps))
        init_time = time.perf_counter()
        for t in apps:
            if not t[0]:
                print(f'应用名不能为空：{t}')
                raise Http404
            if pre_t and pre_t[0] == t[0]:
                for i in range(len(t)):
                    if not t[i]:
                        t[i] = pre_t[i]
            t[4] = "ssh://git@gitlab.zznode.com:2222/zzp/saas/itsaas/" + t[4] + ".git"
            # print(t)
            environments = [env for env in all_envs if env.key == t[2]]
            hosts = [host for host in all_hosts if host.name in t[3].split(",")]
            host_id_list = [host.id for host in hosts]
            # print(f"hosts:{hosts}")
            default_dst_repo = f"/home/{hosts[0].username}/release"
            if not environments:
                print(f'环境不存在：{t[2]}')
                raise Http404
            env = environments[0]
            apps = App.objects.filter(key=t[1]).all()
            app = apps[0] if apps else App()
            app.created_by = user
            app.name = t[0]
            app.key = t[1]
            app.save()
            deploys = [deploy for deploy in all_deploys if deploy.app_id == app.id and deploy.env_id == env.id]
            deploy = deploys[0] if deploys else Deploy()
            deploy.host_ids = host_id_list
            deploy.extend = 1
            deploy.is_audit = 0
            deploy.is_parallel = 0
            deploy.rst_notify = '{"mode":"0"}'
            deploy.app = app
            deploy.created_by = user
            deploy.env = environments[0]
            deploy_save_start = time.perf_counter()
            deploy.save()
            print(f"deploy保存用时：{time.perf_counter()-deploy_save_start:.6f}秒")

            deploy_extend1s = [de for de in all_deploy_extend1s if de.deploy_id == deploy.id]
            deploy_extend1 = deploy_extend1s[0] if deploy_extend1s else DeployExtend1()
            deploy_extend1.deploy = deploy
            deploy_extend1.git_repo = t[4]
            deploy_extend1.dst_dir = t[5]
            deploy_extend1.dst_repo = t[9] if t[9] else default_dst_repo
            deploy_extend1.versions = 5
            if "itsaas-front" in deploy_extend1.git_repo:
                contain_rule = t[8] if t[8] else "favicon.ico\\n index.html\\n static"
                deploy_extend1.filter_rule = '{"type": "contain", "data": "' + contain_rule + '"}'
                compile_project = f"npm i&&npm run build&&mv dist/* ."
                deploy_extend1.hook_post_server = t[6] if t[6] else compile_project
                deploy_extend1.hook_post_host = ''
                deploy_extend1.hook_pre_host = ''
            else:
                contain_rule = t[8] if t[8] else "*.jar"
                deploy_extend1.filter_rule = '{"type": "contain", "data": "' + contain_rule + '"}'
                jar_stop_command = f"bash {t[5]}/run.sh stop 2>/dev/null || echo 'pass'"
                deploy_extend1.hook_pre_host = jar_stop_command if "jar" in contain_rule else ''
                compile_project = f"mvn{t[2]} clean install&&cp target/*.jar ."
                deploy_extend1.hook_post_server = t[6].replace('mvnx', f"mvn{t[2]}") if t[6] else compile_project
                run_command = 'wget http://w.metaitsaas.com/run.sh -o /dev/null\nchmod +x run.sh\n./run.sh -l restart'
                deploy_extend1.hook_post_host = t[7] if t[7] else run_command
            deploy_extend1.save()
            pre_t = t
        final_time = time.perf_counter()
        elapsed_time1 = init_time - start_time
        elapsed_time2 = final_time - init_time
        print(f"初始化耗时：{elapsed_time1:.6f}秒")
        print(f"主程序耗时：{elapsed_time2:.6f}秒")
    return HttpResponse('OK')
