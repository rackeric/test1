from flask import render_template
from flask.views import View


class MainView(View):
    def index(self):
        return render_template('index.html')
