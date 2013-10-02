# -*- coding: utf-8 -*-

"""
                      _ _       _     _
  ___ _ __ ___   __ _(_) |_   _(_)___(_) ___  _ __
 / _ \ '_ ` _ \ / _` | | \ \ / / / __| |/ _ \| '_ \
|  __/ | | | | | (_| | | |\ V /| \__ \ | (_) | | | |
 \___|_| |_| |_|\__,_|_|_| \_/ |_|___/_|\___/|_| |_|

EmailVision REST Client
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Mark A. Richman.
:license: GPL v2, see LICENSE for more details.

Example Usage:

from emailvision.restclient import \
    EMVPlatform, EMVMassUpdate, EMVAPIMergeUploadParams

LOGIN = "YOUR_LOGIN"
PASSWORD = "YOUR_PASSWORD"
KEY = "YOUR_KEY"
client = EMVMassUpdate(EMVPlatform.T5, LOGIN, PASSWORD, KEY)
params = EMVAPIMergeUploadParams()
params.filePath = "/my/path/to/file/"
params.fileName = "test.txt"
params.fileEncoding = "UTF-8"
params.separator = "|"
params.dateFormat = "mm/dd/YYYY"
params.criteria = "LOWER(EMAIL)"  # member field(s) to use as match criteria
params.skipFirstLine = "false"
params.mapping = [{"colNum": 1, "fieldName": "EMAIL"}]
client.mergeUpload(params)

"""

import logging
from requests import Request, Session
import random

__all__ = ["EMVPlatform", "EMVMassUpdate", "EMVAPIMergeUploadParams"]


class EMVPlatform(object):
    """ Pod Hostname (provided by EmailVision) """
    T1 = "emvapi.emv2.com"
    T2 = "p2apic.emv2.com"
    T3 = "p3apic.emv2.com"
    T4 = "p4apic.emv2.com"
    T5 = "p5apic.emv2.com"
    T6 = "p6apic.emv2.com"
    E1 = "emvapi.emv3.com"
    E2 = "p2apie.emv3.com"
    E3 = "p3apie.emv3.com"
    E4 = "p4apie.emv3.com"
    E5 = "p5apie.emv3.com"


class EMVAPIError(object):
    pass


class EMVAPIStreamMethod(object):
    """ HTTP Verb """
    PUT = 100
    GET = 101


class EMVAPIStreamRequestType(object):
    """ HTTP Stream Request Type """
    REGULAR = 200  # GET, HEAD, etc.
    UPSTREAM = 201  # PUT, POST, etc.


class EMVAPIMergeUploadParams(object):
    def __init__(self):
        self.file_path = ''
        self.file_name = ''
        self.file_encoding = "UTF-8"
        self.separator = "|"
        self.date_format = "mm/dd/YYYY"
        self.criteria = "LOWER(EMAIL)"  # field(s) to use as match criteria
        self.skip_first_line = "false"
        self.mapping = []
        self._file_content = ''

    def loadfile(self):
        with open(self.file_path + self.file_name, "rb") as f:
            data = f.read()
            self._file_content = data.encode("base64")


class EMVMassUpdateMapping(object):
    def __init__(self):
        self.column = ''


class EMVAPIStream(object):
    """ API Stream Class """
    def __init__(self):
        self.boundary_seed = str(int(random.random()*1e10))

    def assemble_header(self):
        return "Content-Type: multipart/form-data; boundary=" + \
            self.boundary_seed

    def assemble_upstream_body(self, parameters):
        parameters.load_file()
        output = "--" + self.boundary_seed + "\r\n"
        output += ('''
            Content-Disposition: form-data; name="mergeUpload";
            Content-Type: text/xml
            <?xml version="1.0" encoding="UTF-8"?>
            <mergeUpload>
            <criteria>{}</criteria>
            <fileName>{}</fileName>
            <separator>{}</separator>
            <fileEncoding>{}</fileEncoding>
            <skipFirstLine>{}</skipFirstLine>
            <dateFormat>{}</dateFormat>
            <mapping>''').format(
            parameters.criteria, parameters.file_name, parameters.separator,
            parameters.file_encoding, parameters.skip_first_line,
            parameters.date_format)

        for column in parameters.mapping:
            output += ('''
                <column>
                    <colNum>{}</colNum>
                    <fieldName>{}</fieldName>
                </column>''').format(column['colNum'], column['fieldName'])

        output += "</mapping></mergeUpload"
        output += "\r\n--" + self.boundary_seed + "--\r\n"
        output += "--" + self.boundary_seed + "\r\n"
        output += ('''
        Content-Disposition: form-data; name="inputStream"; filename="%s"
        Content-Type: application/octet-stream
        Content-Transfer-Encoding: base64''') % parameters.file_name
        output += "\r\n" + parameters.file_content
        output += "\r\n--" + self.boundary_seed + "--\r\n"
        return output

    def request(self, url, request_type=EMVAPIStreamRequestType.REGULAR,
                content=None):
        """ Make HTTP Request and return Response """

        #TODO:
        #filepath = 'yourfilename.txt'
        #with open(filepath) as fh:
        #    mydata = fh.read()
        #    response = requests.put(url,
        #            data=mydata,
        #            auth=('omer', 'b01ad0ce'),
        #            headers={'content-type':'text/plain'},
        #            params={'file': filepath})

        session = Session()

        if request_type == EMVAPIStreamRequestType.UPSTREAM:
            request = Request('PUT',
                              url,
                              data=self.assemble_upstream_body(content),
                              headers=self.assemble_header()).prepare()
        else:  # REGULAR
            request = Request('GET', url,
                              data={"max_redirects": 0, "ignore_errors": 1})

        response = session.send(request)
        logging.info(response.status_code)
        return response.content


class EMVAPIStreamResponse(object):
    def __init__(self):
        self.metadata = ''
        self.content = ''


class EMVMassUpdate(object):
    def __init__(self, platform, login, password, key):
        self.login = login
        self.platform = platform
        self.password = password
        self.key = key
        self.token = ''
        self._remoteMethod = ''
        self._parameters = []
        self._stream = EMVAPIStream()
        self.open_connection()

    def __del__(self):
        self.close_connection()

    def get_url_endpoint(self, remote_method, parameters=None):
        output = "http://{}/apibatchmember/services/rest/{}".format(
            self.platform, remote_method)
        if parameters is not None:
            output += "?" + urlencode(parameters)
        return output

    def open_connection(self):
        url = self.get_url_endpoint("connect/open", {
            "login": self.login,
            "password": self.password,
            "key": self.key}
        )
        response = self._stream.request(url)
        self.token = response.result[0]

    def close_connection(self):
        url = self.get_url_endpoint("connect/close" + self.token)
        self._stream.request(url, EMVAPIStreamMethod.GET,
                             EMVAPIStreamRequestType.REGULAR)

    def merge_upload(self, parameters):
        url = self.get_url_endpoint("batchmemberservice" + self.token +
                                    "/batchmember/mergeUpload")
        self._stream.request(url, EMVAPIStreamRequestType.UPSTREAM, parameters)
