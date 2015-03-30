from threading import Thread

from app import app
from snmp import views


t = Thread(target=views.run_server)
t.start()

app.run()



