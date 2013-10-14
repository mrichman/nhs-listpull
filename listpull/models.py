from datetime import datetime

from listpull import db


class Job(db.Model):
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
        self.csv = csv

    def __repr__(self):
        return '<Job {}>'.format(self.id)


class ListType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<ListType {}>'.format(self.name)
