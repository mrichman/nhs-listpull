#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import logging
import requests
import httplib
import os

from mom import MOMClient
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
from urllib import urlencode
from xml.etree import ElementTree as et
from xml.dom.minidom import parseString

httplib.HTTPConnection.debuglevel = 1  # or 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.ERROR)
requests_log.propagate = True

URL = "http://p3apic.emv2.com/apibatchmember/services/rest/"
LOGIN = "API_ACCESS"
PASSWORD = "Nutr1-health"
KEY = "CdX7Cr9n3XiwsGN-dfEc0bSyTC4DZNiyhlylS5kHLeD7G8-ZvA"
OPEN_URL = URL + "connect/open"
CLOSE_URL = URL + "connect/close"

credentials = urlencode({"login": LOGIN, "password": PASSWORD, "key": KEY})

# Open API session
r = requests.get(OPEN_URL + "?" + credentials)
tree = et.fromstring(r.content)
token = tree[0].text
logging.info("Token: " + token)

# http://atlee.ca/software/poster/index.html
register_openers()

insert_upload_url = URL + "batchmemberservice/" + token + \
    "/batchmember/insertUpload"

# Define Column Mapping XML
insertUpload = et.Element("insertUpload")
criteria = et.SubElement(insertUpload, "criteria")
criteria.text = 'LOWER(EMAIL)'
fileName = et.SubElement(insertUpload, "fileName")
fileName.text = 'listpull.csv'
separator = et.SubElement(insertUpload, "separator")
separator.text = ','
dateFormat = et.SubElement(insertUpload, "dateFormat")
dateFormat.text = 'MM/dd/YYYY'
mapping = et.SubElement(insertUpload, "mapping")
columns = {"0": "CUSTNUM", "1": "FIRSTNAME", "2": "LASTNAME", "3": "EMAIL"}
for k, v in columns.iteritems():
    column = et.SubElement(mapping, "column")
    colNum = et.SubElement(column, "colNum")
    colNum.text = k
    fieldName = et.SubElement(column, "fieldName")
    fieldName.text = v
tree = et.ElementTree(insertUpload)
root = tree.getroot()
data = et.tostring(root)
logging.debug(parseString(data).toprettyxml())

# Get customer data from MOM as CSV
try:
    config = os.path.join(os.path.dirname(__file__), 'config.ini')
    mom = MOMClient(config)
    customer_data = mom.get_customers()
except Exception as e:
    logging.error("Error: " + e.message)
    exit(1)

# Base64-encode CSV Data
#with open('/tmp/email.csv', 'rb') as fd:
#    b64data = base64.b64encode(fd.read())
b64data = base64.b64encode(customer_data)

uri = '/apibatchmember/services/rest/batchmemberservice/' + token + \
      "/batchmember/insertUpload"
x = [MultipartParam('insertUpload', value=data,
                    filetype="text/xml; charset=utf8"),
     MultipartParam('inputStream', value=b64data, filename='email.csv',
                    filetype="application/octet-stream")]
encData, encHeaders = multipart_encode(x)

# Upload file
try:
    logging.info("Upload URL: " + insert_upload_url)
    upload_res = requests.put(insert_upload_url, headers=encHeaders,
                              data=''.join(encData))
    logging.info("Status: " + str(upload_res.status_code))
    if upload_res.status_code != 200:
        logging.info("Reason: " + upload_res.reason)
    else:
        logging.info("Response: " + upload_res.text)
        tree = et.fromstring(upload_res.content)
        job_id = tree[0].text
        logging.info("Job ID: " + job_id)
except Exception as e:
        logging.error("Error: " + e.message)

# Close API session
close_res = requests.get(CLOSE_URL + "/" + token)
logging.info("Status: " + str(close_res.status_code))
logging.info("Response: " + close_res.text)
