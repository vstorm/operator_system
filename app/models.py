from datetime import datetime

import rrdtool

from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

SSH_PASSWORD = 0
SSH_KEY = 1


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True,
                         nullable=False)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    alarm_email = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)
    is_activate = db.Column(db.Boolean, default=False)
    last_login_time = db.Column(db.DateTime)
    register_time = db.Column(db.DateTime, default=datetime.utcnow())

    # group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    # users_servers(many to many)
    servers = db.relationship('Server', secondary='users_servers',
                              backref=db.backref('users', lazy='dynamic'))

    # users_serverGroups(many to many)
    server_groups = db.relationship('ServerGroup', secondary='users_server_groups',
                                    backref=db.backref('users', lazy='dynamic'))

    # users_remoteUser (many to many)
    remote_user = db.relationship('RemoteUser', secondary='users_remote_users',
                                  backref=db.backref('users', lazy='dynamic'))

    # def __init__(self, username, first_name, last_name, password, email,
    #              alarm_email, is_admin, is_active, last_login_time, register_time):
    #     self.username = username
    #     self.password = hashlib.md5.update(password.encode()).hexdigest()
    #     self.email = email

    ops = db.relationship('OpsLogs', backref='user', lazy='dynamic')
    ops_tem = db.relationship('OpsLogsTem', backref='user', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return self.username


# class Group(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     group_name = db.Column(db.String(40), unique=True,
#                           nullable=False)
#     users = db.relationship('User', backref='group', lazy='dynamic')
#
#     def __repr__(self):
#         return '<Group {0}>'.format(self.group_name)


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(40), unique=True,
                         nullable=False)
    ip = db.Column(db.String(30), unique=True,
                   nullable=False)
    port = db.Column(db.Integer, nullable=False)
    operation_system = db.Column(db.String(20), nullable=False)
    status_monitor_on = db.Column(db.BOOLEAN)
    #snmp
    snmp_on = db.Column(db.BOOLEAN)
    snmp_version = db.Column(db.String(10))
    snmp_security_level = db.Column(db.String(20))
    snmp_community_name = db.Column(db.String(20))
    snmp_auth_protocol = db.Column(db.String(20))
    snmp_user = db.Column(db.String(30))
    snmp_password = db.Column(db.String(30))
    system_load_critical = db.Column(db.BOOLEAN)
    load = db.Column(db.Float, default=0)
    cpu_idle_critical = db.Column(db.BOOLEAN)
    cpu_idle = db.Column(db.Integer, default=0)
    mem_usage_critical = db.Column(db.BOOLEAN)
    mem_usage = db.Column(db.Integer, default=0)

    server_group_id = db.Column(db.Integer, db.ForeignKey('server_group.id', ondelete='CASCADE'))
    ops_temp = db.relationship('OpsLogsTem', backref='server', lazy='dynamic')
    remote_user = db.relationship('ServerRemoteUser', backref='server', lazy='dynamic')
    status = db.relationship('ServerStatus', backref='server', uselist=False)

    def __repr__(self):
        return '{0} {1}'.format(self.hostname, self.ip)

    def create_rrdtool(self):
        data_sources = ['DS:memory:GAUGE:600:U:U',
                        'DS:cpu:GAUGE:600:U:U',
                        'DS:load:GAUGE:600:U:U']
        db_name = 'rrdtool/' + self.ip + '.rrd'
        current_time = str(int(datetime.now().timestamp()))
        rrdtool.create(db_name,
                       '--start', current_time,
                       data_sources,
                       'RRA:AVERAGE:0.5:1:600',
                       'RRA:AVERAGE:0.5:6:7000',
                       'RRA:AVERAGE:0.5:24:775',
                       'RRA:AVERAGE:0.5:288:797')


class ServerStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean)
    ping_status = db.Column(db.String(100))
    up_since = db.Column(db.DateTime)
    last_check = db.Column(db.DateTime)

    server_id = db.Column(db.Integer, db.ForeignKey('server.id', ondelete='CASCADE'))


class ServerGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(40), unique=True,
                           nullable=False)

    servers = db.relationship('Server', backref='server_group', lazy='dynamic')

    def __repr__(self):
        return self.group_name


class RemoteUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remote_username = db.Column(db.String(30), unique=True,
                                nullable=False)

    # # remoteUsers_servers (many to many)
    # servers = db.relationship('Server', secondary='remote_users_servers',
    #                           backref=db.backref('remote_users', lazy='dynamic'))
    server = db.relationship('ServerRemoteUser', backref='remote_user', lazy='dynamic')

    def __repr__(self):
        return self.remote_username


class AuthType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.SmallInteger, default=SSH_PASSWORD)
    name = db.Column(db.String(20), unique=True, nullable=False)

    server_remote_user = db.relationship('ServerRemoteUser', backref='auth_type', lazy='dynamic')

    def __repr__(self):
        return self.name


class ServerRemoteUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id', ondelete='CASCADE'))
    remote_user_id = db.Column(db.Integer, db.ForeignKey('remote_user.id', ondelete='CASCADE'))
    auth_type_id = db.Column(db.Integer, db.ForeignKey('auth_type.id', ondelete='CASCADE'))
    auth_password = db.Column(db.String(50))

    # def __repr__(self):
    #     return 'Server {0}, Remote_user {1}'.format()

    # server = db.relationship('Server', backref='server', lazy='dynamic')


# users_servers(many to many) actual table
users_servers = db.Table('users_servers',
                         db.Column('user_id', db.Integer,
                                   db.ForeignKey('user.id', ondelete='CASCADE')),
                         db.Column('server_id', db.Integer, db.ForeignKey('server.id',
                                                                          ondelete='CASCADE')))

# users_serverGroups(many to many) actual table
users_server_groups = db.Table('users_server_groups',
                               db.Column('user_id', db.Integer, db.ForeignKey('user.id',
                                                                              ondelete='CASCADE')),
                               db.Column('server_group_id', db.Integer,
                                         db.ForeignKey('server_group.id',
                                                       ondelete='CASCADE')))

# # remoteUsers_servers (many to many) actual table
# remote_users_servers = db.Table('remote_users_servers',
#                                 db.Column('remote_user_id', db.Integer,
#                                           db.ForeignKey('remote_user.id',
#                                                         ondelete='CASCADE')),
#                                 db.Column('server_id', db.Integer,
#                                           db.ForeignKey('server.id',
#                                                         ondelete='CASCADE')),
#                                 db.Column('auth_type', db.Integer, db.ForeignKey('auth_type.id',
#                                                                                  ondelete='CASCADE')),
#                                 db.Column('auth_password', db.String(50)))

# users_remoteUser (many to many) actual table
users_remote_users = db.Table('users_remote_users',
                              db.Column('user_id', db.Integer,
                                        db.ForeignKey('user.id',
                                                      ondelete='CASCADE')),
                              db.Column('remote_user_id', db.Integer,
                                        db.ForeignKey('remote_user.id',
                                                      ondelete='CASCADE')))


class OpsLogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_mark = db.Column(db.Integer, unique=True)
    remote_user = db.Column(db.String(40))
    cmd = db.Column(db.String(70))
    total_num = db.Column(db.Integer)
    success_num = db.Column(db.Integer)
    fail_num = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    finish_time = db.Column(db.DateTime)
    log_type = db.Column(db.String(30))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


    def __repr__(self):
        return 'ops_log {0}'.format(self.id)

    def get_track_mark(self):
        return str(self.track_mark)

    def __init__(self, user, remote_user, cmd, total_num, success_num, fail_num,
                 start_time, finish_time, log_type, track_mark):
        self.user_id = user.id
        self.remote_user = remote_user.remote_username
        self.cmd = cmd
        self.total_num = total_num
        self.success_num = success_num
        self.fail_num = fail_num
        self.start_time = start_time
        self.finish_time = finish_time
        self.log_type = log_type
        self.track_mark = track_mark


class OpsLogsTem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_mark = db.Column(db.Integer)
    cmd = db.Column(db.String(70))
    event_type = db.Column(db.String(30))
    event_log = db.Column(db.String(120))
    result = db.Column(db.Boolean)

    server_id = db.Column(db.Integer, db.ForeignKey('server.id',
                                                    ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',
                                                  ondelete='CASCADE'))


    def __repr__(self):
        return '<User {0} execute {1}'.format(self.user, self.cmd) + \
               'successfully' if self.result else 'fail' + '>'

    def __init__(self, user, server, cmd, event_type, event_log, result, track_mark):
        self.user_id = user.id
        self.server_id = server.id
        self.cmd = cmd
        self.event_type = event_type
        self.event_log = event_log
        self.result = result
        self.track_mark = track_mark


