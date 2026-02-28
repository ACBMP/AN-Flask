import socket
import os
import psutil
import requests
import subprocess
ACB2_SERVER = "147.93.4.239"
#ips = {
#        "ACB 2.0 Online Config Service": [ACB2_SERVER, 80, "tcp"],
#        "ACB 2.0 Authentication": [ACB2_SERVER, 21030, "udp"],
#        "ACB 2.0 Matchmaking": [ACB2_SERVER, 21031, "udp"],
#        }

processes = {
        "Matchmaking Bot": "python3 queue_bot.py",
        "Main Bot": "python3 bot.py",
        }


def check_tcp(host, port, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def check_udp(host, port):
    try:
        return "open|" in subprocess.getoutput(f"/usr/bin/nmap --privileged -sU -p {port} {host}")
    except:
        return False

def check_process(name):
    return name in (" ".join(p.cmdline()) for p in psutil.process_iter(attrs=['cmdline']))

def check_ocs(host):
    url = f"http://{host}/OnlineConfigService.svc/GetOnlineConfig"
    params = {"onlineConfigID": "ACB"}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return True
    return False

def main():
    statuses = {}
    statuses["ACB 2.0 Server"] = check_ocs(ACB2_SERVER)
    #for k in ips.keys():
    #    if ips[k][2] == "tcp":
    #        statuses[k] = check_tcp(ips[k][0], ips[k][1])
    #    else:
    #        statuses[k] = check_udp(ips[k][0], ips[k][1])
    for k, v in processes.items():
        statuses[k] = check_process(v)
    # convert form dict to list for laziness reasons
    s = []
    for k in statuses.keys():
        s.append({"name": k, "status": statuses[k]})
    return s
