#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import StringIO
import time

from ConfigParser import SafeConfigParser
from flask import Flask, request, g, render_template, flash, send_file
from mom import MOMClient
from zlib import compress, decompress

app = Flask(__name__)

app.config.update(dict(
    DATABASE='/tmp/nhs-listpull.db',
    DEBUG=True,
    SECRET_KEY='\xeb\x12A;\x8b\x0c$\xf4>O\xb6\x9c\x15y=>\x0cU<Kzp>\xe9',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('NHS-LISTPULL_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    app.logger.info("Initializing database")
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            sql = f.read()
            app.logger.debug(sql)
            db.cursor().executescript(sql)
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_mom():
    """Opens a new MOM db connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mom'):
        config_ini = os.path.join(os.path.dirname(__file__), 'config.ini')
        config = SafeConfigParser()
        config.read(config_ini)
        mom_host = config.get("momdb", "host")
        mom_user = config.get("momdb", "user")
        mom_password = config.get("momdb", "password")
        mom_database = config.get("momdb", "db")
        g.mom = MOMClient(mom_host, mom_user, mom_password, mom_database)
    return g.mom


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def show_jobs():
    app.logger.debug("show_jobs()")
    db = get_db()
    cur = db.execute('select * from job_status order by id desc')
    jobs = cur.fetchall()
    app.logger.debug("Found {} jobs".format(len(jobs)))
    return render_template('show_entries.html', jobs=jobs)

@app.route('/list', methods=['POST'])
def create_list():
    # curl --data "list_type_id=1" http://localhost:5000/list
    app.logger.debug("create_list()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    mom = get_mom()
    csv, count = mom.get_customers()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    db = get_db()
    db.execute(('insert into job_status '
               '(list_type_id, record_count, status, csv) VALUES (?,?,?,?)'),
               (list_type_id, count, 0, csv))
    db.commit()
    flash('List successfully generated with {} records'.format(count))
    return show_jobs()

@app.route('/csv/<int:job_id>', methods=['GET'])
def get_csv(job_id):
    db = get_db()
    cur = db.execute('select csv from job_status where id = {}'.format(job_id))
    csv = cur.fetchone()[0]
    csv = decompress(csv)
    sio = StringIO.StringIO()
    sio.write(csv)
    sio.seek(0)
    return send_file(sio,
                     attachment_filename=
                     "{}_{}.txt".format(job_id, time.strftime("%Y%m%d%H%M%S")),
                     as_attachment=True)

if __name__ == '__main__':
    app.logger.debug(__name__)
    #init_db()
    app.run()
