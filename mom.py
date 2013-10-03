#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MOM SQL Server Client
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Mark A. Richman.
:license: GPL v2, see LICENSE for more details.

Example Usage:

from mom import MOMClient

config = os.path.join(os.path.dirname(__file__), 'config.ini')
mom = MOMClient(config)
csv = mom.get_customers()
"""

import logging

from csv import Error, writer
from io import BytesIO
from pymssql import connect, InterfaceError


class MOMClient(object):
    """ MOM SQL Client """
    def __init__(self, host, user, password, database):
        self.conn = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def get_mom_connection(self):
        """ Gets SQL Server connection to MOM """
        try:
            logging.info('Connecting to MOM...')
            if self.conn is None:
                self.conn = connect(host=self.host,
                                    user=self.user,
                                    password=self.password,
                                    database=self.database,
                                    as_dict=False)
            return self.conn
        except InterfaceError as error:
            msg = "Error connecting to SQL Server: %s" % error.message
            logging.error(msg)
            raise Exception(msg)
        except Exception as e:
            logging.error(e.message)
            raise

    def get_customers(self):
        """
        Get all customers from MOM, including Autoship customers, but excluding
        opt-outs and Amazon emails. Returns CSV.
        """
        bio = BytesIO()
        try:
            conn = self.get_mom_connection()
            cur = conn.cursor()
            logging.info("ListPull_GetAllCustomers")
            cur.execute("exec ListPull_GetAllCustomers")
            data = cur.fetchall()
            [writer(bio).writerow(row) for row in data]
        except Error as e:
            logging.error(e)
            raise
        except Exception as ex:
            logging.error(ex.message)
            raise
        return bio.getvalue()
