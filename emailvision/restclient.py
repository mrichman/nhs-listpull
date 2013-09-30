# -*- coding: utf-8 -*-

"""
Example Usage:

LOGIN = "YOUR_LOGIN"
PASSWORD = "YOUR_PASSWORD"
KEY = "YOUR_KEY"
client = EMVMassUpdate(EMVPlatform.T5, LOGIN, PASSWORD, KEY)
params = new EMVAPIMergeUploadParams()
params.filePath = "/my/path/to/file/"
params.fileName = "test.txt"
params.fileEncoding = "UTF-8"
params.separator = "|"
params.dateFormat = "mm/dd/YYYY"
params.criteria = "LOWER(EMAIL)"  # member field(s) to use as match criteria
params.skipFirstLine = "false"
params.mapping = [{"colNum": 1, "fieldName": "EMAIL}]
client.mergeUpload(params)

"""

import hashlib
from urllib import urlencode
from uuid import uuid1


class EMVPlatform(object):
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
    PUT = 100
    GET = 101


class EMVAPIStreamRequestType(object):
    REGULAR = 200
    UPSTREAM = 201


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
        self.boundary_seed = hashlib.md5(uuid1("5AFF8C33A03")).hexdigest()

    def assemble_header(self):
        return "Content-Type: multipart/form-data; boundary=" + \
            self.boundary_seed

    def assemble_upstream_body(self, parameters):
        pass

    def request(self, url, method=EMVAPIStreamMethod.GET,
                request_type=EMVAPIStreamRequestType.REGULAR, content=None):
        pass


class EMVAPIStreamResponse(object):
    def __init__(self):
        self.metadata = ''
        self.response = ''


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

    def get_url_endpoint(self, remote_method, parameters=None):
        output = "http://" + self.platform + \
                 "/apibatchmember/services/rest/" + \
                 remote_method
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
        pass

    def merge_upload(self, parameters):
        pass
