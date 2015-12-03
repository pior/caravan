import httpretty


def setUpModule():
    httpretty.HTTPretty.allow_net_connect = False
