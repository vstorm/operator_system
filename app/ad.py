from flask import redirect, url_for, flash
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import AdminIndexView, expose
from wtforms import PasswordField
from wtforms.validators import required, Email, Length, EqualTo, IPAddress
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext import login
from flask.ext.admin import Admin

from app import app, db
from app.forms import AdminLoginForm
from app.models import User, Server, ServerGroup, RemoteUser, OpsLogs, OpsLogsTem, AuthType, ServerRemoteUser, \
    ServerStatus


class AuthView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


class UserView(AuthView):
    can_create = True

    column_list = ('username', 'email', 'alarm_email', 'is_admin', 'is_staff', 'is_activate', 'last_login_time')
    column_searchable_list = ('username', 'email')
    # column_labels = dict(is_activate='is_active')
    # column_descriptions = dict(
    #     username='First and Last name'
    # )
    column_filters = ('username', 'last_login_time')
    # column_select_related_list = ('servers',)

    form_columns = ('username', 'first_name', 'last_name', 'password',
                    'confirm', 'email', 'alarm_email', 'is_admin', 'is_activate',
                    'servers', 'server_groups', 'remote_user', 'register_time')
    form_args = dict(
        username=dict(validators=[required(),
                                  Length(min=5, max=20)]),
        password=dict(validators=[Length(min=6, max=20)]),
        email=dict(validators=[Email()]),
        alarm_email=dict(validators=[Email()])
    )
    form_overrides = dict(password=PasswordField)
    form_extra_fields = {
        'confirm': PasswordField('repeat password',
                                 validators=[required(),
                                             EqualTo('confirm', message='Passwords must match')])
    }

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UserView, self).__init__(User, session, **kwargs)

    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(form.password.data)

        # def create_model(self, form):
        #     password = form.password.data
        #     form.password.data = md5(password.encode()).hexdigest()
        #     return True


class ServerView(AuthView):
    # Override displayed fields
    column_list = ('hostname', 'ip', 'port', 'operation_system', 'status_monitor_on', 'snmp_on')
    # column_searchable_list = ('hostname', 'ip')
    column_filters = ('hostname', 'ip')

    form_excluded_columns = ('users', 'remote_user', 'ops_temp', 'status')
    form_args = dict(
        ip=dict(validators=[IPAddress()])
    )
    # form_overrides = dict(users=SelectMultipleField)


    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(ServerView, self).__init__(Server, session, **kwargs)

    def after_model_change(self, form, model, is_created):
        if is_created:
            model.create_rrdtool()


class ServerGroupView(AuthView):
    form_columns = ('group_name',)

    form_args = dict(
        group_name=dict(validators=[Length(min=5, max=10)]),
    )

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(ServerGroupView, self).__init__(ServerGroup, session, **kwargs)


class RemoteUserView(AuthView):
    form_columns = ('remote_username',)

    form_args = dict(
        remote_username=dict(validators=[Length(min=3, max=10)]),
    )

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(RemoteUserView, self).__init__(RemoteUser, session, **kwargs)


class AuthTypeView(AuthView):
    column_list = ('name', )

    form_excluded_columns = ('server_remote_user',)

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(AuthTypeView, self).__init__(AuthType, session, **kwargs)


class ServerRemoteUserView(AuthView):
    column_list = ('server', 'remote_user', 'auth_type', 'auth_password')
    column_sortable_list = (('server', Server.ip), )
    column_filters = ('server.hostname', 'server.ip',)

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(ServerRemoteUserView, self).__init__(ServerRemoteUser, session, **kwargs)


class OpsLogsView(AuthView):
    column_display_pk = True
    column_list = ('user', 'remote_user', 'cmd', 'log_type', 'total_num', 'success_num', 'fail_num',
                   'start_time', 'finish_time', 'track_mark')
    # column_labels = dict(id='track mark')
    column_filters = ('user.username',)
    column_sortable_list = (('user', User.username), 'start_time')

    form_excluded_columns = ('temp',)

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(OpsLogsView, self).__init__(OpsLogs, session, **kwargs)


class OpsLogsTemView(AuthView):
    column_list = ('user', 'server.hostname', 'server.ip',
                   'event_type', 'event_log', 'result', 'track_mark')

    # column_labels = dict(opslog_id='track mark')
    column_filters = ('user.username', 'server.hostname', 'server.ip')
    column_sortable_list = (('user', User.username), 'server.hostname', 'server.ip', 'track_mark')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(OpsLogsTemView, self).__init__(OpsLogsTem, session, **kwargs)


class ServerStatusView(AuthView):
    def __init__(self, session, **kwargs):
        super(ServerStatusView, self).__init__(ServerStatus, session, **kwargs)


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()
    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = AdminLoginForm()
        if form.validate_on_submit():
            user = form.user.data
            password = form.password.data
            u = User.query.filter_by(username=user).first()
            # print(user, password,u.username, u.password)
            if u and check_password_hash(u.password, password):
                login.login_user(u)
            else:
                flash('invalid username or password')
        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        return self.render('admin/index.html', form=form)

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


admin = Admin(app, 'Auth', index_view=MyAdminIndexView(), base_template='admin/auth.html')

admin.add_view(UserView(db.session))
admin.add_view(ServerView(db.session))
admin.add_view(ServerGroupView(db.session))
admin.add_view(RemoteUserView(db.session))
admin.add_view(AuthTypeView(db.session))
admin.add_view(ServerRemoteUserView(db.session))
admin.add_view(ServerStatusView(db.session))
admin.add_view(OpsLogsView(db.session))
admin.add_view(OpsLogsTemView(db.session))