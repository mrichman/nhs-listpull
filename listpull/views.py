# -*- coding: utf-8 -*-

""" Flask Views """

import time
from zlib import compress, decompress
from StringIO import StringIO

from flask import request, render_template, flash, redirect, send_file

from . import app, db, mom, sf
from listpull import utils
from .models import Job, ListType, Product, Category, category_product


@app.route('/')
def show_jobs():
    """
    Get all Jobs.
    """
    app.logger.debug("show_jobs()")
    jobs = db.session.query(Job).\
        join(ListType).\
        filter(Job.list_type_id == ListType.id).\
        order_by(Job.id.desc()).\
        all()
    app.logger.debug("Found {} jobs".format(len(jobs)))
    categories = db.session.query(Category).all()
    products = db.session.query(Product).all()
    return render_template('jobs.html', jobs=jobs, categories=categories,
                           products=products)


@app.route('/list', methods=['POST'])
def create_list():
    """
    Entire House File + Autoships.
    """
    app.logger.debug("create_list()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    app.logger.debug("mom.get_customers()")
    try:
        csv, count = mom.get_customers()
    except Exception as e:
        app.logger.error(e.message)
        flash(e.message, 'danger')
        return redirect('/')
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    if 'include_prev_list' in request.form:  # absent when unchecked
        app.logger.debug("include_prev_list=True")
        csv = utils.merge_previous_list(csv, list_type_id)
    csv = compress(csv)
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    job = Job(list_type_id=list_type_id, record_count=count, csv=csv)
    db.session.add(job)
    db.session.commit()
    flash('Generated list with {:,} records'.format(count), "success")
    return redirect('/')


@app.route('/list-noas', methods=['POST'])
def create_list_no_autoship():
    """
    Entire House File (No Autoships).
    """
    app.logger.debug("create_list_no_autoship()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    app.logger.debug("mom.get_customers_excl_autoship()")
    csv, count = mom.get_customers_excl_autoship()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    csv = buffer(compress(csv))
    if 'include_prev_list' in request.form:  # absent when unchecked
        app.logger.debug("include_prev_list=True")
        csv = utils.merge_previous_list(csv, list_type_id)
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    job = Job(list_type_id=list_type_id, record_count=count, csv=csv)
    db.session.add(job)
    db.session.commit()
    flash('List successfully generated with {:,} records'.format(count),
          "success")
    return redirect('/')


@app.route('/list-reengagement', methods=['POST'])
def create_list_reengagement():
    """
    Re-engagement File (Non-Autoship Customers idle > 120 days).
    """
    app.logger.debug("create_list_reengagement()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    app.logger.debug("mom.get_customers_reengagement()")
    csv, count = mom.get_customers_reengagement()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    if 'include_prev_list' in request.form:  # absent when unchecked
        app.logger.debug("include_prev_list=True")
        csv = utils.merge_previous_list(csv, list_type_id)
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    job = Job(list_type_id=list_type_id, record_count=count, csv=csv)
    db.session.add(job)
    db.session.commit()
    flash('List successfully generated with {:,} records'.format(count),
          "success")
    return redirect('/')


@app.route('/csv/<int:job_id>', methods=['GET'])
def get_csv(job_id):
    """
    Action to retrieve the compressed CSV from the database.
    :param job_id: int
    """
    job = db.session.query(Job).filter_by(id=job_id).first()
    if job.compressed_csv is None:
        flash("No data available.", "danger")
        return redirect('/')
    # app.logger.info("CSV {}".format(job.compressed_csv))
    csv = decompress(job.compressed_csv)
    sio = StringIO()
    sio.write(csv)
    sio.seek(0)
    return send_file(sio,
                     attachment_filename=
                     "{}_{}.txt".format(job_id, time.strftime("%Y%m%d%H%M%S")),
                     as_attachment=True)


@app.route('/send/<int:job_id>', methods=['GET'])
def send_to_smartfocus(job_id):
    """
    Sends raw CSV to SmartFocus.
    :param job_id: int
    """
    job = db.session.query(Job).filter_by(id=job_id).first()
    if job.compressed_csv is None:
        flash("No data available.", "danger")
        return redirect('/')
    csv = decompress(job.compressed_csv)
    column_mapping = utils.get_column_mapping(job.list_type_id)
    app.logger.info("Sending {} bytes of CSV to SmartFocus".format(len(csv)))
    sf_job_id = sf.insert_upload(csv, column_mapping)
    if sf_job_id > 0:
        job = db.session.query(Job).filter_by(id=job_id).first()
        job.sf_job_id = sf_job_id
        job.status = 1
        db.session.commit()
        flash("List successfully sent to SmartFocus (Job ID {}).".format(
            sf_job_id), "success")
    else:
        flash("Something went horribly wrong.", "danger")
    return redirect('/')


@app.route('/delete/<int:job_id>', methods=['GET'])
def delete_job(job_id):
    """
    Delete a job.
    :param job_id: int
    """
    try:
        job = db.session.query(Job).filter_by(id=job_id).first()
        db.session.delete(job)
        db.session.commit()
        flash("Job {} successfully deleted".format(job_id), "success")
    except Exception as e:
        flash("Something went horribly wrong. {}".format(e), "danger")
    return redirect('/')


@app.route('/list-as', methods=['POST'])
def create_list_autoships():
    """
    Autoship Customers Only.
    """
    app.logger.debug("create_list_autoships()")
    list_type_id = request.form['list_type_id']
    app.logger.debug("list_type_id=" + list_type_id)
    app.logger.debug("mom.get_autoships()")
    csv, count = mom.get_autoships()
    app.logger.debug("CSV is {} bytes".format(len(csv)))
    if 'include_prev_list' in request.form:  # absent when unchecked
        app.logger.debug("include_prev_list=True")
        csv = utils.merge_previous_list(csv, list_type_id)
    csv = buffer(compress(csv))
    app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
    job = Job(list_type_id=list_type_id, record_count=count, csv=csv)
    db.session.add(job)
    db.session.commit()
    flash('List successfully generated with {:,} records'.format(count),
          "success")
    return redirect('/')


@app.route('/list-cat-x-sell', methods=['POST'])
def create_list_cat_x_sell():
    """
    Category Cross-Sell Emails.
    Get all products from selected category, then remove the ones from
    product_list. Send resultant set of product ids to sproc to retrieve
    customer list
    """
    app.logger.debug("create_list_cat_x_sell()")
    list_type_id = request.form['list_type_id']
    category_id = request.form['category']
    exclude_product_list = request.form.getlist('products')
    app.logger.debug("list_type_id=" + list_type_id)
    app.logger.debug("category_id={}".format(category_id))
    app.logger.debug("product_list=" + ','.join(exclude_product_list))

    products = [p.sku for p in
                db.session.query(Product.sku).join(category_product).
                filter(Category.id == category_id).
                filter(~Product.id.in_(exclude_product_list)).
                all()]

    app.logger.debug(products)
    app.logger.debug("mom.get_cat_x_sell()")
    try:
        csv, count = mom.get_cat_x_sell(products)
        app.logger.debug("CSV is {} bytes".format(len(csv)))
        if len(csv) == 0:
            flash("No data found.", "warning")
            return redirect('/')
        if 'include_prev_list' in request.form:  # absent when unchecked
            app.logger.debug("include_prev_list=True")
            csv = utils.merge_previous_list(csv, list_type_id)
        csv = buffer(compress(csv))
        app.logger.debug("Compressed CSV is {} bytes".format(len(csv)))
        job = Job(list_type_id=list_type_id, record_count=count, csv=csv)
        db.session.add(job)
        db.session.commit()
        flash('List successfully generated with {:,} records'.format(count),
              "success")
    except Exception as e:
        flash("Something went horribly wrong. {}".format(e), "danger")
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    """
    Page Not Found.
    :param e:
    """
    return render_template('templates/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """
    Internal Server Error.
    :param e:
    """
    return render_template('templates/500.html'), 500


@app.template_filter()
def datetimeformat(datetime):
    """
    Template filter for datetime.
    """
    return datetime.strftime('%Y-%m-%d %H:%M:%S')
