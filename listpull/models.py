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
    sf_job_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    compressed_csv = db.Column(db.LargeBinary)

    def __init__(self, list_type, created_at=None):
        self.list_type = list_type
        if created_at is None:
            created_at = datetime.utcnow()
        self.created_at = created_at

    def __repr__(self):
        return '<Job {}>'.format(self.id)


class ListType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<ListType {}>'.format(self.name)
