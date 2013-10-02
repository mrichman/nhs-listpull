#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import logging
import requests
from urllib import urlencode
from xml.etree import ElementTree
import httplib

httplib.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

URL = "http://p3apic.emv2.com/apibatchmember/services/rest/"

OPEN_URL = URL + "connect/open"
CLOSE_URL = URL + "connect/close"

credentials = urlencode({"login": LOGIN, "password": PASSWORD, "key": KEY})

# Open API session
r = requests.get(OPEN_URL + "?" + credentials)
tree = ElementTree.fromstring(r.content)
token = tree[0].text
print("Token: " + token)

with open('/Users/mark.richman/email.csv', 'rb') as fd:
     b64data = base64.b64encode(fd.read())

files = {'file': ('email.csv', b64data, 'application/octet-stream')}

#files = {'file': ('email.csv',
#                  open('/Users/mark.richman/email.csv', 'rb').
#                  read().encode("base64"))}

insert_upload_url = URL + "batchmemberservice/" + token + \
    "/batchmember/insertUpload"

data = '''<?xml version="1.0" encoding="UTF-8"?>
<insertUpload>
    <criteria>LOWER(EMAIL)</criteria>
    <fileName>email.csv</fileName>
    <separator>,</separator>
    <fileEncoding>UTF-8</fileEncoding>
    <skipFirstLine>false</skipFirstLine>
    <dateFormat>mm/dd/YYYY</dateFormat>
    <mapping>
        <column>
            <colNum>0</colNum>
            <fieldName>CUSTNUM</colNum>
        <column>
        <column>
            <colNum>1</colNum>
            <fieldName>FIRSTNAME</colNum>
        <column>
        <column>
            <colNum>2</colNum>
            <fieldName>LASTNAME</colNum>
        <column>
        <column>
            <colNum>3</colNum>
            <fieldName>EMAIL</colNum>
        <column>
    </mapping>
</insertUpload>'''


# Upload file
try:
    logging.info("Upload URL: " + insert_upload_url)
    headers = {'Content-type': 'multipart/form-data'}
    upload_res = requests.put(insert_upload_url, files=files,
                              data={'insertUpload': data}, headers=headers)
    logging.info("Status: " + str(upload_res.status_code))
    if upload_res.status_code != requests.codes.ok:
        logging.info("Reason: " + upload_res.reason)
    else:
        logging.info("Response: " + upload_res.text)
except Exception as e:
    logging.info("Error: " + e.message)

# Close API session
close_res = requests.get(CLOSE_URL + "/" + token)
logging.info("Status: " + str(close_res.status_code))
logging.info("Response: " + close_res.text)
