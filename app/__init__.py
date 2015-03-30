from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.admin import Admin
from flask.ext.login import LoginManager
from flask_bootstrap import Bootstrap

# from app.ad import MyAdminIndexView

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)



lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

Bootstrap(app)

from app import views, models, ad
