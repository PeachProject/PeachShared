import serviceListUpdateConsumer
from subprocess import call
import library.config.peachSharedConfig
import os

def start():
    #start consumer
    fileToOpen = os.path.dirname(os.path.realpath(__file__)) + "/serviceListUpdateConsumer.py"
    kafka = library.config.peachSharedConfig.get_server_address("kafka")
    event = library.config.peachSharedConfig.get_event("serviceList")
    temp = library.config.peachSharedConfig.get_service_temp_file()
    schema = library.config.peachSharedConfig.schema_file("service")
    cmd = "python '" + fileToOpen + "' --ka '" + kafka + "' --ev '" + event + "' --temp '" + temp + "' --s '" + schema + "'"
    #call(["gnome-terminal"])
    cmds = ["gnome-terminal", "-x", "sh", "-c", "\"" + cmd + "\"", ]
    raw = " ".join(cmds)
    print(raw)
    call(raw, shell=True)