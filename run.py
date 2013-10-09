#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sqlite3
import StringIO
import time

from ConfigParser import SafeConfigParser
from emailvision.restclient import RESTClient
from flask import Flask, request, g, render_template, flash, send_file, \
    redirect
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


def get_ev_client():
    """Gets an instance of the EmailVision REST client."""
    if not hasattr(g, 'ev'):
        config_ini = os.path.join(os.path.dirname(__file__), 'config.ini')
        config = SafeConfigParser()
        config.read(config_ini)
        ev_url = config.get("emailvision", "url")
        ev_login = config.get("emailvision", "login")
        ev_password = config.get("emailvision", "password")
        ev_key = config.get("emailvision", "key")
        g.ev = RESTClient(ev_url, ev_login, ev_password, ev_key)
    return g.ev


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if error is not None:
        app.logger.error(error)
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
    sql = '''
        select j.id, j.record_count, j.ev_job_id,
        j.created_at, j.csv, t.name,
        case
            when j.status = 0 then 'Pending'
            when j.status = 1 then 'Complete'
        end status
        from job_status j
        inner join list_types t on (j.list_type_id = t.id)
        order by j.id desc'''
    cur = db.execute(sql)
    jobs = cur.fetchall()
    app.logger.debug("Found {} jobs".format(len(jobs)))
    return render_template('job_status.html', jobs=jobs)


@app.route('/list', methods=['POST'])
def create_list():
    # curl --data "list_type_id=1" http://localhost:5000/list
    app.logger.debug("create_list()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    mom = get_mom()
    app.logger.debug("mom.get_customers()")
    csv, count = mom.get_customers()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    db = get_db()
    db.execute(('insert into job_status '
               '(list_type_id, record_count, status, csv) VALUES (?,?,?,?)'),
               (list_type_id, count, 0, csv))
    db.commit()
    flash('List successfully generated with {:,} records'.format(count))
    return redirect('/')


@app.route('/list-noas', methods=['POST'])
def create_list_no_autoship():
    app.logger.debug("create_list_no_autoship()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    mom = get_mom()
    app.logger.debug("mom.get_customers_excl_autoship()")
    csv, count = mom.get_customers_excl_autoship()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    db = get_db()
    db.execute(('insert into job_status '
               '(list_type_id, record_count, status, csv) VALUES (?,?,?,?)'),
               (list_type_id, count, 0, csv))
    db.commit()
    flash('List successfully generated with {:,} records'.format(count))
    return redirect('/')


@app.route('/list-reengagement', methods=['POST'])
def create_list_reengagement():
    app.logger.debug("create_list_reengagement()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    mom = get_mom()
    app.logger.debug("mom.get_customers_reengagement()")
    csv, count = mom.get_customers_reengagement()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    db = get_db()
    db.execute(('insert into job_status '
               '(list_type_id, record_count, status, csv) VALUES (?,?,?,?)'),
               (list_type_id, count, 0, csv))
    db.commit()
    flash('List successfully generated with {:,} records'.format(count))
    return redirect('/')


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


@app.route('/send/<int:job_id>', methods=['GET'])
def send_to_emailvision(job_id):
    """ Sends raw CSV to EmailVision """
    db = get_db()
    cur = db.execute('select csv from job_status where id = {}'.format(job_id))
    csv = cur.fetchone()[0]
    logging.info("Got {} bytes of compressed CSV".format(len(csv)))
    csv = decompress(csv)
    logging.info("Sending {} bytes of raw CSV to EmailVision".format(len(csv)))
    ev_job_id = get_ev_client().insert_upload(csv)
    if ev_job_id > 0:
        db.execute('update job_status set ev_job_id = ?, status=1 '
                   'where id = ?', (ev_job_id, job_id))
        db.commit()
        flash("List successfully sent to EmailVision (Job ID {}).".format(
            ev_job_id))
    else:
        flash("Something went horribly wrong.", "error")
    return redirect('/')


@app.route('/delete/<int:job_id>', methods=['GET'])
def delete_job(job_id):
    """Delete a job"""
    try:
        db = get_db()
        db.execute('delete from job_status where id = {}'.format(job_id))
        db.commit()
        flash("Job {} successfully deleted".format(job_id))
    except Exception as e:
        flash("Something went horribly wrong. {}".format(e), "error")
    return redirect('/')


@app.route('/list-as', methods=['POST'])
def create_list_autoships():
    app.logger.debug("create_list_autoships()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    app.logger.debug("mom.get_autoships()")
    csv, count = get_mom().get_autoships()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    db = get_db()
    db.execute(('insert into job_status '
               '(list_type_id, record_count, status, csv) VALUES (?,?,?,?)'),
               (list_type_id, count, 0, csv))
    db.commit()
    flash('List successfully generated with {:,} records'.format(count))
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html', e=e), 500

if __name__ == '__main__':
    app.logger.debug(__name__)
    #init_db()
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='nhs-listpull.log', level=logging.DEBUG,
                        format=FORMAT)
    app.run()
