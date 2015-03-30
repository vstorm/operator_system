import os
from multiprocessing.pool import Pool
from functools import reduce
from datetime import datetime
from sqlalchemy.exc import InvalidRequestError, IntegrityError

import paramiko
import rrdtool
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db, lm
from app.forms import LoginForm, PasswordForm, ProfileForm
from app.models import User, ServerRemoteUser, RemoteUser, Server, OpsLogs
from app.log import write_ops, write_ops_tem

from config import PROCESS_NUMBER

track_num = 0


@lm.user_loader
def load_user(uid):
    return User.query.get(int(uid))


@app.before_first_request
def before_first_request():
    global track_num
    ops = OpsLogs.query.order_by('-track_mark').first()
    if ops:
        track_num = ops.track_mark


@app.before_request
def before_request():
    g.user = current_user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        username, password = form.username.data, form.password.data
        user = User.query.filter_by(username=username).first()
        # assert False
        if user is not None and check_password_hash(user.password, password):
            remember_me = session['remember_me']
            login_user(user, remember=remember_me)
            user.last_login_time = datetime.now()
            db.session.commit()
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Invalid username or wrong password!')
    return render_template('login.html',
                           form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
@app.route('/index')
@login_required
def index():
    server_groups = g.user.server_groups
    servers = g.user.servers
    own_server = reduce(lambda x, y: x + y, [s.servers.all() for s in server_groups]) if server_groups else [] + servers
    return render_template('index.html',
                           servers=own_server)


@app.route('/server_resource', methods=['POST'])
@login_required
def resource():
    db_name = 'rrdtool/' + request.form.get('server') + ".rrd"
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    resolution = request.form.get('resolution')
    # type = request.form.get('type')
    print(db_name, start_time, end_time)
    data = rrdtool.fetch(db_name, 'AVERAGE',  '-s {0}'.format(start_time), '-e {0}'.format(end_time))

    # if type == "load":
    #     d = data[2]
    # elif type == "cpu":
    #     d = data[1]
    # elif type == 'memory':
    #     d = data[0]

    data = list(zip(*data[2]))

    memory = list(map(lambda x: int(x) if x is not None else 0, data[0]))[:-2]
    cpu = list(map(lambda x: int(x) if x is not None else 0, data[1]))[:-2]
    load = list(map(lambda x: round(x, 2) if x is not None else 0, data[2]))[:-2]

    # print(data)
    return jsonify({
        'data': {'memory': memory,
                 'cpu': cpu,
                 'load': load}
    })


@app.route('/cmd')
@login_required
def cmd():
    server_groups = g.user.server_groups
    servers = g.user.servers
    remote_users = g.user.remote_user
    return render_template('cmd.html',
                           server_groups=server_groups,
                           servers=servers,
                           remote_users=remote_users)


@app.route('/execute_cmd', methods=['POST'])
@login_required
def execute_cmd():
    global track_num
    # pool.apply_async()
    servers_id_list = request.form.getlist('servers')
    remote_user_id = request.form.get('remote_user')
    command = request.form.get('command')
    servers_id_list = list(set(servers_id_list))

    # get auth and no_auth
    remote_user = RemoteUser.query.get(remote_user_id)
    server_remote_user = []
    event_type = 'CommandExcution'
    event_log = 'no auth in server'
    msg = {"success": [], "fail": []}
    mark = track_num + 1
    track_num += 1
    result = False
    for server_id in servers_id_list:
        s = ServerRemoteUser.query.filter_by(server=Server.query.get(server_id),
                                             remote_user=remote_user).first()
        if s:
            server_remote_user.append(s)
        else:
            no_auth_server = Server.query.get(server_id)
            msg['fail'].append(no_auth_server.ip)
            write_ops_tem(g.user, no_auth_server, command, event_type, event_log, result, mark)

    # multiprocessing to execute command
    results = []
    pool = Pool(PROCESS_NUMBER)
    uid = g.user.id
    user = User.query.get(uid)
    print(mark)
    for s in server_remote_user:
        server = s.server
        results.append(pool.apply_async(ssh_cmd, args=(
            server, user, remote_user.remote_username, s.auth_password,
            command, s.auth_type.name, mark)))
    pool.close()
    pool.join()

    # get the result
    total_num = len(servers_id_list)
    success_num = 0
    fail_num = total_num - len(server_remote_user)
    start_time = datetime.now()
    for r in results:
        message = r.get()
        print(message)
        if message[3]:
            success_num += 1
            msg['success'].append(message[0])
        else:
            fail_num += 1
            msg['fail'].append(message[0])

    finish_time = datetime.now()
    log_type = 'BatchRunCommand'
    write_ops(g.user, remote_user, command, total_num,
              success_num, fail_num, start_time, finish_time, log_type, mark)

    return jsonify(msg)


@app.route('/file')
@login_required
def file():
    server_groups = g.user.server_groups
    servers = g.user.servers
    remote_users = g.user.remote_user
    files_info = get_file_info()
    # print(files)
    return render_template('file.html',
                           server_groups=server_groups,
                           servers=servers,
                           remote_users=remote_users,
                           files_info=files_info)


def get_file_info():
    files_info = [(file, os.stat(os.path.join(dirpath, file)).st_size) for (dirpath, dirnames, filenames) in
                  os.walk('filesend') for file in filenames]
    # print(files_info)
    return files_info


@app.route('/transfer_file', methods=['POST'])
@login_required
def transfer_file():
    global track_num
    # pool.apply_async()
    servers_id_list = request.form.getlist('servers')
    remote_user_id = request.form.get('remote_user')
    trans_type = request.form.get('trans_type')
    remote_path = request.form.get('remote_path')
    servers_id_list = list(set(servers_id_list))

    if trans_type == 'getfile':
        files = request.form.get('files')
        event_type = 'GetFile'
        log_type = 'BatchGetFile'
        total_num = len(servers_id_list)
    else:
        files = request.form.getlist('files')
        event_type = 'SendFile'
        log_type = 'BatchSendFile'
        total_num = len(servers_id_list) * len(files)

    msg = {"success": [], "fail": []}
    remote_user = RemoteUser.query.get(remote_user_id)
    mark = track_num + 1
    track_num += 1
    server_remote_user = []
    for server_id in servers_id_list:
        s = ServerRemoteUser.query.filter_by(server=Server.query.get(server_id),
                                             remote_user=remote_user).first()
        if s:
            server_remote_user.append(s)
        else:
            result = False
            no_auth_server = Server.query.get(server_id)
            if trans_type == 'getfile':
                log = 'get {0} from {1} '.format(files, no_auth_server.ip)
                event_log = log + 'no auth user'
                msg["fail"].append(log)
                write_ops_tem(g.user, no_auth_server, '', event_type, event_log, result, mark)
            else:
                for f in files:
                    log = 'send {0} to {1} '.format(f, no_auth_server.ip)
                    event_log = log + 'no auth user'
                    msg['fail'].append(log)
                    write_ops_tem(g.user, no_auth_server, '', event_type, event_log, result, mark)

    uid = g.user.id
    user = User.query.get(uid)
    results = []
    pool = Pool(PROCESS_NUMBER)
    start_time = datetime.now()
    for s in server_remote_user:
        server = s.server
        results.append(pool.apply_async(ssh_file, args=(
            server, user, remote_user.remote_username, s.auth_password,
            files, remote_path, s.auth_type.name, trans_type, mark)))

    pool.close()
    pool.join()

    for r in results:
        message = r.get()
        print(message)
        msg['fail'].extend(message['fail'])
        msg['success'].extend(message['success'])
    finish_time = datetime.now()
    write_ops(g.user, remote_user, "", total_num,
              len(msg['success']), len(msg['fail']), start_time, finish_time, log_type, mark)
    return jsonify(msg)


def ssh_cmd(server, user, username, auth, command, auth_type, mark):
    ip = server.ip
    port = server.port
    ssh = paramiko.SSHClient()
    # know_hosts
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if auth_type == 'SSH-PASSWORD':
        ssh.connect(ip, port=port, username=username, password=auth)
    else:
        private_key = paramiko.RSAKey.from_private_key_file(auth)
        ssh.connect(ip, port=port, username=username, pkey=private_key)
    stdin, stdout, stderr = ssh.exec_command(command)
    out = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    ssh.close()
    event_type = 'CommandExcution'
    if stdout.channel.recv_exit_status() == 0:
        result = True
        event_log = out
    else:
        result = False
        event_log = error
    write_ops_tem(user, server, command, event_type, event_log, result, mark)
    return ip, out, error, result


def ssh_file(server, user, username, auth, files, remote_path, auth_type, tran_type, mark):
    # print(ip, port, username, auth, files, auth_type, tran_type)
    ip = server.ip
    port = server.port
    scp = paramiko.Transport((ip, port))
    if auth_type == 'SSH-PASSWORD':
        scp.connect(username=username, password=auth)
    else:
        private_key = paramiko.RSAKey.from_private_key_file(auth)
        scp.connect(username=username, pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(scp)
    return_code = {'success': [], 'fail': []}
    if tran_type == 'sendfile':
        event_type = "SendFile"
        for f in files:
            local_file = 'filesend/' + f
            remote_file = '{0}/{1}'.format(remote_path, f)
            event_log = 'sending file {0} to {1}'.format(f, ip)
            try:
                sftp.mkdir(remote_path)
            except IOError:
                pass
            # print(local_file,remote_file)
            try:
                sftp.put(local_file, remote_file)
                result = True
                return_code['success'].append(event_log)
            except Exception:
                result = False
                return_code['fail'].append(event_log)
            write_ops_tem(user, server, '', event_type, event_log, result, mark)
    else:
        event_type = "GetFile"
        remote_file = remote_path.split('/')[-1]
        local_file = '{0}/{1}'.format("filerev", remote_file)
        event_log = 'get file {0} from {1}'.format(remote_file, ip)
        try:
            sftp.get(remote_path, local_file)
            result = True
            return_code['success'].append(event_log)
        except Exception:
            result = False
            return_code['fail'].append(event_log)
        write_ops_tem(user, server, '', event_type, event_log, result, mark)
    sftp.close()
    scp.close()

    return return_code
    # event_type = 'FileTransport'


@app.route('/server_status')
@login_required
def server_status():
    servers = g.user.servers
    server_groups = g.user.server_groups
    if list(server_groups):
        s = reduce(lambda x, y: x.servers.all() + y.servers.all(), server_groups)
    else:
        s = []
    servers = list(set(servers + s))
    return render_template('status.html', servers=servers)


@app.route('/ops_log')
@login_required
def ops_log():
    ops_logs = g.user.ops
    return render_template('ops.html', ops_logs=ops_logs)


@app.route('/ops_log_tem')
@login_required
def ops_log_tem():
    ops_logs_tem = g.user.ops_tem
    return render_template('ops_tem.html', ops_logs_tem=ops_logs_tem)


@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html')


@app.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    form = PasswordForm()
    if form.validate_on_submit():
        new_password = form.password.data
        g.user.password = generate_password_hash(new_password)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('password.html', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        alarm_email = form.alarm_email.data
        try:
            g.user.username = username
            g.user.email = email
            g.user.alarm_email = alarm_email
            db.session.commit()
            return redirect(url_for('index'))

        except (InvalidRequestError, IntegrityError):
            flash('Duplicate username!')
            db.session.rollback()

    form.username.data = g.user.username
    form.email.data = g.user.email
    form.alarm_email.data = g.user.alarm_email
    return render_template('edit_profile.html', form=form)

