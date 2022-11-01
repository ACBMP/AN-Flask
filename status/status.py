# acb pc login ips from wireshark captures
ips = {"PC Login A": "216.98.48.133", "PC Login B": "216.98.55.165"}

def test_server(ip):
    """
    test a server for availability via simple pinging
    """
    import os
    return not os.system("ping -c 1 -w 2 " + ip)

# https://www.ubisoft.com/en-au/help/game/assassins-creed-brotherhood just parses this json
url = "https://game-status-api.ubisoft.com/v1/instances?appIds=a2296d44-5ea3-430e-bdc5-9771cea01531,6e2c60d5-594f-438b-af2d-72a8184198fe,95c47b46-067e-41e8-aaeb-d7cfa4148526,e421a897-4eb7-45a7-a4dc-6aaf4d7bd8a9"

def official_status(url, statuses={}):
    """
    https://stackoverflow.com/a/50360059
    """
    import urllib.request
    import json
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    data = json.load(resp)

    for platform in data:
        statuses[platform["Platform"]] = platform["Status"] == "Online"

    return statuses

def main():
    statuses = {}
    print("Testing game servers via official status page...")
    statuses = official_status(url, statuses)
    print("Testing PC login servers...")
    for k in ips.keys():
        statuses[k] = test_server(ips[k])
    # convert form dict to list for laziness reasons
    s = []
    for k in statuses.keys():
        s.append({"name": k, "status": statuses[k]})
    return s
