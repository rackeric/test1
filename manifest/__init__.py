from flask import Flask
from celery import Celery
from config import config
from views import MainView
from tasks import AnsibleJeneric

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    celery = make_celery(app)

    # old API routes
    # url(r"^ansible_jeneric/(?P<user_id>\d+)/(?P<project_id>-.*-*.*)/(?P<job_id>-.*-*.*)", 'destinyCelery.ansible_jeneric_view'),
    # url(r"^ansible_playbook/(?P<user_id>\d+)/(?P<project_id>-.*-*.*)/(?P<playbook_id>-.*-*.*)", 'destinyCelery.ansible_playbook_view'),
    # url(r"^ansible_playbook_manual/(?P<user_id>\d+)/(?P<project_id>-.*-*.*)/(?P<playbook_id>-.*-*.*)", 'destinyCelery.ansible_playbook_manual_view'),
    # url(r"^rax_create_server/(?P<user_id>\d+)/(?P<project_id>-.*-*.*)/(?P<job_id>-.*-*.*)", 'destinyCelery.rax_create_server_view'),

    app.add_url_rule('/', view_func=MainView.as_view('main_view'))

    app.add_url_rule('/api/v1/ansible_jeneric/<string:user_id>/<string:project_id>/<string:job_id>',
                     view_func=AnsibleJeneric.as_view('ansible_jeneric'))


    return app
