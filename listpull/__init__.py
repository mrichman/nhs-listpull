# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103

""" listpull module """

import logging

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from mom.client import SQLClient
from smartfocus.restclient import RESTClient
from formatters import ColorFormatter

app = Flask(__name__)
app.config.from_object('config')

logging.getLogger("").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(ColorFormatter())
logging.getLogger("").addHandler(consoleHandler)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

mom = SQLClient(app.config['MOM_HOST'],
                app.config['MOM_USER'],
                app.config['MOM_PASSWORD'],
                app.config['MOM_DB'])

sf = RESTClient(app.config['SMARTFOCUS_URL'],
                app.config['SMARTFOCUS_LOGIN'],
                app.config['SMARTFOCUS_PASSWORD'],
                app.config['SMARTFOCUS_KEY'])

import listpull.models
import listpull.views
