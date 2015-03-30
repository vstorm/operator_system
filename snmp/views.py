import time
from datetime import datetime
from subprocess import Popen, PIPE
from collections import OrderedDict

import rrdtool

from app import db
from app.models import Server, ServerStatus


# s = scheduler(time.time, time.sleep)

def server_status():
    results = []
    for server in Server.query.all():
        r = get_server_status(server)
        results.append((server, r))

    for result in results:
        server = result[0]
        r = result[1]
        r.wait()
        output = r.stdout.read()  # will block
        return_code = r.returncode
        # print(server, return_code)
        status = ServerStatus.query.filter_by(server_id=server.id).first()
        if not status:
            s = ServerStatus()
            s.server = server
            s.up_since = datetime.now()
            status = s
            db.session.add(s)
            db.session.commit()
        if return_code == 0:
            status.status = True
            status.ping_status = output.decode('utf-8').splitlines()[-1]
        else:
            status.status = False
            status.ping_status = ''
        status.last_check = datetime.now()
        db.session.commit()


def get_server_status(server):
    ip = server.ip
    return Popen(["ping", "-c 1", ip], stdout=PIPE, stderr=PIPE)


def server_resource():
    results = []
    for server in Server.query.all():
        if server.status.status:
            skip = (('system_load', ".1.3.6.1.4.1.2021.10.1.3.2"),
                    ("idle_cpu_time", ".1.3.6.1.4.1.2021.11.11.0"),
                    ("total_memory", ".1.3.6.1.4.1.2021.4.5.0"),
                    ("total_memory_free", ".1.3.6.1.4.1.2021.4.6.0"))
            oids = OrderedDict(skip)
            oids = " ".join(list(oids.values()))
            cmd = "snmpget -v2c -c public {0} {1} | awk {2}".format(server.ip, oids, "'{print $4}'")
            r = get_server_resource(cmd)
            results.append((server, r))

    for result in results:
        server = result[0]
        r = result[1]
        r.wait()
        return_code = r.returncode
        output = r.stdout.read()
        if output:
            output = output.decode('utf-8').splitlines()
            # print(output)
            system_load, idle_cpu_time, total_memory, total_memory_free = map(float, output)
            memory_used_pecentage = int((total_memory - total_memory_free) / total_memory * 100)
            print(memory_used_pecentage)
            used_cpu_time = int(100 - idle_cpu_time)
            db_name = 'rrdtool/' + server.ip + '.rrd'
            now = datetime.now().timestamp()
            # print(total_memory, idle_cpu_time, system_load, total_memory_free)
            # print(db_name, memory_used_pecentage, used_cpu_time, system_load)
            rrdtool.update(db_name, "{0}:{1}:{2}:{3}".format(now, memory_used_pecentage,
                                                             used_cpu_time, system_load))


def get_server_resource(cmd):
    return Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)


def run_server():
    while True:
        print('begin to collect' + str(datetime.now().timestamp()))
        server_status()
        server_resource()
        time.sleep(300)
