#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import httplib

from ConfigParser import SafeConfigParser
from emailvision.restclient import RESTClient
from mom import MOMClient


def main():
    httplib.HTTPConnection.debuglevel = 0  # or 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.ERROR)
    requests_log.propagate = True
    config_ini = os.path.join(os.path.dirname(__file__), 'config.ini')
    config = SafeConfigParser()
    config.read(config_ini)
    mom_host = config.get("momdb", "host")
    mom_user = config.get("momdb", "user")
    mom_password = config.get("momdb", "password")
    mom_database = config.get("momdb", "db")
    ev_url = config.get("emailvision", "url")
    ev_login = config.get("emailvision", "login")
    ev_password = config.get("emailvision", "password")
    ev_key = config.get("emailvision", "key")
    ev = RESTClient(ev_url, ev_login, ev_password, ev_key)
    mom = MOMClient(mom_host, mom_user, mom_password, mom_database)
    csv = mom.get_customers()
    job_id = ev.insert_upload(csv)
    print("Job ID: " + job_id)

if __name__ == '__main__':
    main()