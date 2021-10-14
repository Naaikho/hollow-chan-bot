# -*- coding: utf-8 -*-

import os, sys
import time

def isConnected(try_ping, client, info):
    time.sleep(10)
    while try_ping:
        import subprocess
        ping = subprocess.Popen(["ping", "-c", "1", "www.google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = ping.communicate()
        del out
        if (not client.is_ready()) and err == b'' and try_ping:
            os.system("python3 -m pip install -U discord.py")
            os.execv(sys.executable, [sys.executable, sys.path[0]+"/start.py"] + sys.argv)
        elif err != b'':
            if info == "test":
                    print(str(err))
            elif info == "serv":
                print("pc restart . . .")
                time.sleep(5)
                os.system("shutdown /r /t 1")
        time.sleep(10)