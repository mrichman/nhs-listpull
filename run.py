#!/usr/bin/env python
# -*- coding: utf-8 -*-

from listpull import app


if __name__ == '__main__':
    app.run()

# app.run(threaded=True, host='0.0.0.0', port=80, debug=True)
# sudo gunicorn -D -b 10.139.16.14:80 run:app
