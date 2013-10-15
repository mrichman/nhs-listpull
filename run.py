#!/usr/bin/env python
# -*- coding: utf-8 -*-

from listpull import app


app.run(threaded=True, host='0.0.0.0', port=80, debug=True)
