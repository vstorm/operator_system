"""empty message

Revision ID: b78aa84831
Revises: 3ebdfd86934
Create Date: 2014-05-08 19:35:02.053641

"""

# revision identifiers, used by Alembic.
revision = 'b78aa84831'
down_revision = '3ebdfd86934'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('server_group')
    op.drop_table('server_remote_user')
    op.drop_table('users_remote_users')
    op.drop_table('ops_logs')
    op.drop_table('user')
    op.drop_table('users_servers')
    op.drop_table('server')
    op.drop_table('auth_type')
    op.drop_table('users_server_groups')
    op.drop_table('ops_logs_tem')
    op.drop_table('remote_user')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('remote_user',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('remote_username', mysql.VARCHAR(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('ops_logs_tem',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('cmd', mysql.VARCHAR(length=70), nullable=True),
    sa.Column('event_type', mysql.VARCHAR(length=30), nullable=True),
    sa.Column('event_log', mysql.VARCHAR(length=120), nullable=True),
    sa.Column('result', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('server_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('opslog_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['opslog_id'], ['ops_logs.id'], name='ops_logs_tem_ibfk_3', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], name='ops_logs_tem_ibfk_1', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='ops_logs_tem_ibfk_2', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('users_server_groups',
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('server_group_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['server_group_id'], ['server_group.id'], name='users_server_groups_ibfk_2', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='users_server_groups_ibfk_1', ondelete='CASCADE'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('auth_type',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('type', mysql.SMALLINT(display_width=6), autoincrement=False, nullable=True),
    sa.Column('name', mysql.VARCHAR(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('server',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('hostname', mysql.VARCHAR(length=40), nullable=False),
    sa.Column('ip', mysql.VARCHAR(length=30), nullable=False),
    sa.Column('port', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('operation_system', mysql.VARCHAR(length=20), nullable=False),
    sa.Column('status_monitor_on', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('snmp_on', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('snmp_version', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('snmp_security_level', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('snmp_community_name', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('snmp_auth_protocol', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('snmp_user', mysql.VARCHAR(length=30), nullable=True),
    sa.Column('snmp_password', mysql.VARCHAR(length=30), nullable=True),
    sa.Column('system_load_critical', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('load', mysql.FLOAT(), nullable=True),
    sa.Column('cpu_idle_critical', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('cpu_idle', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('mem_usage_critical', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('mem_usage', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('server_group_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['server_group_id'], ['server_group.id'], name='server_ibfk_1', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('users_servers',
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('server_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], name='users_servers_ibfk_2', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='users_servers_ibfk_1', ondelete='CASCADE'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('user',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('username', mysql.VARCHAR(length=40), nullable=False),
    sa.Column('first_name', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('last_name', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('password', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('alarm_email', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('is_admin', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('is_staff', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('is_activate', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('last_login_time', mysql.DATETIME(), nullable=True),
    sa.Column('register_time', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('ops_logs',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('remote_user', mysql.VARCHAR(length=40), nullable=True),
    sa.Column('cmd', mysql.VARCHAR(length=70), nullable=True),
    sa.Column('total_num', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('success_num', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('fail_num', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('start_time', mysql.DATETIME(), nullable=True),
    sa.Column('finish_time', mysql.DATETIME(), nullable=True),
    sa.Column('log_type', mysql.VARCHAR(length=30), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='ops_logs_ibfk_1', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('users_remote_users',
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('remote_user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['remote_user_id'], ['remote_user.id'], name='users_remote_users_ibfk_2', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='users_remote_users_ibfk_1', ondelete='CASCADE'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('server_remote_user',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('server_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('remote_user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('auth_type_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('auth_password', mysql.VARCHAR(length=50), nullable=True),
    sa.ForeignKeyConstraint(['auth_type_id'], ['auth_type.id'], name='server_remote_user_ibfk_3', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['remote_user_id'], ['remote_user.id'], name='server_remote_user_ibfk_2', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], name='server_remote_user_ibfk_1', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('server_group',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('group_name', mysql.VARCHAR(length=40), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    ### end Alembic commands ###
