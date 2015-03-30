# development
import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
# for mysql connection
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:lqf19911129@" \
                          "localhost/operation"
# for database migration
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SECRET_KEY = "ifq\xd6X0\xc7iS\xc1\x031\xb1\x1aD%\x97\xbf\xfdx\xd3\r\xcb\x8f"

BOOTSTRAP_SERVE_LOCAL = True

PROCESS_NUMBER = 10