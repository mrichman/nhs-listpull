# -*- coding: utf-8 -*-

""" Flask Models """

from datetime import datetime

from listpull import db


class Job(db.Model):
    """ SQLAlchemy Job Model """
    id = db.Column(db.Integer, primary_key=True)
    list_type_id = db.Column(db.Integer, db.ForeignKey('list_type.id'),
                             nullable=False)
    list_type = db.relationship('ListType',
                                backref=db.backref('jobs', lazy='dynamic'))
    record_count = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    sf_job_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    compressed_csv = db.Column(db.LargeBinary)

    def __init__(self, list_type_id, record_count=0, status=0, sf_job_id=0,
                 csv=None, created_at=datetime.utcnow()):
        self.list_type_id = list_type_id
        self.created_at = created_at
        self.record_count = record_count
        self.status = status
        self.sf_job_id = sf_job_id
        self.compressed_csv = csv

    def __repr__(self):
        return '<Job {}>'.format(self.id)


class ListType(db.Model):
    """ SQLAlchemy ListType Model """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<ListType {}>'.format(self.name)


category_product = db.Table('category_product',
                            db.Column('category_id',
                                      db.Integer,
                                      db.ForeignKey('category.id')),
                            db.Column('product_id',
                                      db.Integer,
                                      db.ForeignKey('product.id')))


class Product(db.Model):
    """ SQLAlchemy Product Model """
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    categories = db.relationship('Category', secondary=category_product,
                                 backref=db.backref('products',
                                                    lazy='dynamic'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Product {}>'.format(self.name)


class Category(db.Model):
    """ SQLAlchemy Category Model """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category {}>'.format(self.name)
