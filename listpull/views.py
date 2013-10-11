# -*- coding: utf-8 -*-

import logging
import time
from zlib import compress, decompress
from StringIO import StringIO

from flask import request, render_template, flash, redirect, send_file

from . import app, db, mom, sf
from .models import Job


@app.route('/')
def show_jobs():
    app.logger.debug("show_jobs()")
    #sql = '''
    #    select j.id, j.record_count, j.ev_job_id,
    #    j.created_at, j.csv, t.name,
    #    case
    #        when j.status = 0 then 'Pending'
    #        when j.status = 1 then 'Complete'
    #    end status
    #    from job_status j
    #    inner join list_types t on (j.list_type_id = t.id)
    #    order by j.id desc'''
    #cur = db.execute(sql)
    #jobs = cur.fetchall()
    jobs = Job.query.all()
    app.logger.debug("Found {} jobs".format(len(jobs)))
    return render_template('jobs.html', jobs=jobs)


@app.route('/list', methods=['POST'])
def create_list():
    # curl --data "list_type_id=1" http://localhost:5000/list
    app.logger.debug("create_list()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    app.logger.debug("mom.get_customers()")
    csv, count = mom.get_customers()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
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
    app.logger.debug("mom.get_customers_excl_autoship()")
    csv, count = mom.get_customers_excl_autoship()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
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
    app.logger.debug("mom.get_customers_reengagement()")
    csv, count = mom.get_customers_reengagement()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    db.execute(('insert into job_status '
               '(list_type_id, record_count, status, csv) VALUES (?,?,?,?)'),
               (list_type_id, count, 0, csv))
    db.commit()
    flash('List successfully generated with {:,} records'.format(count))
    return redirect('/')


@app.route('/csv/<int:job_id>', methods=['GET'])
def get_csv(job_id):
    cur = db.execute('select csv from job_status where id = {}'.format(job_id))
    csv = cur.fetchone()[0]
    csv = decompress(csv)
    sio = StringIO()
    sio.write(csv)
    sio.seek(0)
    return send_file(sio,
                     attachment_filename=
                     "{}_{}.txt".format(job_id, time.strftime("%Y%m%d%H%M%S")),
                     as_attachment=True)


@app.route('/send/<int:job_id>', methods=['GET'])
def send_to_smartfocus(job_id):
    """ Sends raw CSV to SmartFocus """
    cur = db.execute('select csv from job_status where id = {}'.format(job_id))
    csv = cur.fetchone()[0]
    logging.info("Got {} bytes of compressed CSV".format(len(csv)))
    csv = decompress(csv)
    logging.info("Sending {} bytes of raw CSV to SmartFocus".format(len(csv)))
    ev_job_id = sf.insert_upload(csv)
    if ev_job_id > 0:
        db.execute('update job_status set ev_job_id = ?, status=1 '
                   'where id = ?', (ev_job_id, job_id))
        db.commit()
        flash("List successfully sent to SmartFocus (Job ID {}).".format(
            ev_job_id))
    else:
        flash("Something went horribly wrong.", "error")
    return redirect('/')


@app.route('/delete/<int:job_id>', methods=['GET'])
def delete_job(job_id):
    """Delete a job"""
    try:
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
    csv, count = mom.get_autoships()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    db.execute(('insert into job_status '
               '(list_type_id, record_count, status, csv) VALUES (?,?,?,?)'),
               (list_type_id, count, 0, csv))
    db.commit()
    flash('List successfully generated with {:,} records'.format(count))
    return redirect('/')


@app.route('/list-cat-x-sell', methods=['POST'])
def create_list_cat_x_sell():
    app.logger.debug("create_list_cat_x_sell()")
    list_type_id = request.form['list_type_id']
    category_list = request.form.getlist('category-list')
    product_list = request.form.getlist('product-list')
    app.logger.debug("list_type_id=" + list_type_id)
    app.logger.debug("category_list=" + ','.join(category_list))
    app.logger.debug("product_list=" + ','.join(product_list))
    app.logger.debug("mom.get_cat_x_sell()")
    csv, count = mom.get_cat_x_sell()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    db.execute(('insert into job_status '
               '(list_type_id, record_count, status, csv) VALUES (?,?,?,?)'),
               (list_type_id, count, 0, csv))
    db.commit()
    flash('List successfully generated with {:,} records'.format(count))
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('templates/404.html', e=e), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('templates/500.html', e=e), 500
