#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Flask Shell
"""

import os
import readline
from pprint import pprint

from flask import *
from listpull import *

os.environ['PYTHONINSPECT'] = 'True'
