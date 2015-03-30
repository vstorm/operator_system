from app import db
from app.models import OpsLogs, OpsLogsTem


def write_ops(user, remote_user, command, total_num,
              success_num, fail_num, start_time, finish_time, log_type, track_mark):
    ops = OpsLogs(user, remote_user, command, total_num,
                  success_num, fail_num, start_time, finish_time, log_type, track_mark)
    db.session.add(ops)
    db.session.commit()

def write_ops_tem(user, server, command, event_type, event_log, result, track_mark):
    ops_tem = OpsLogsTem(user, server, command, event_type, event_log, result, track_mark)
    db.session.add(ops_tem)
    db.session.commit()
