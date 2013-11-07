# -*- coding: utf-8 -*-

import logging

from StringIO import StringIO
from io import BytesIO
from csv import reader, writer
from zlib import decompress
from listpull.models import Job


def extract_emails_from_csv(csv_data):
    """
    Given CSV formatted input, return a list of all email addresses. This
    function assumes emails are in the first column.
    :type csv_data: str or unicode
    """
    emails = []
    f = StringIO(csv_data)
    for row in reader(f, delimiter=','):
        emails.append(row[0])
    return emails


def remove_rows_containing_emails(csv_data, emails):
    """
    Given CSV formatted input, remove rows with matching emails. This
    function assumes emails are in the first column.

    Args:
        csv_data: CSV data
        emails: list of email addresses
    Returns:
        list of email addresses (usually smaller than emails)
    Raises:
        UnicodeEncodeError:
        Exception:
    """
    bio = BytesIO()
    count = 0
    try:
        for row in reader(csv_data):
            if row[0] not in emails:
                # Write to new csv
                writer(bio).writerow([unicode(s).encode() for s in row])
                count += 1
    except UnicodeEncodeError as uee:
        logging.error(uee)
        raise
    except Exception as ex:
        logging.error(ex.message)
        raise
    return bio.getvalue()


def merge_previous_list(csv_data, list_type_id):
    """
    Merges the most recent list from app.db of type list_type_id
    and merges into csv_data.

    Args:
        csv_data: CSV data
        list_type_id: List type
    Returns:
        list of email addresses (usually larger than csv_data)
    Raises:
        Exception:
    """
    job = Job.previous_by_list_type_id(list_type_id)
    prev_csv = decompress(job.compressed_csv)
    seen = set()  # set for fast O(1) amortized lookup
    new_sio = StringIO(csv_data)
    for row in reader(new_sio):
        seen.add(row[0])
    old_sio = StringIO(prev_csv)
    for row in reader(old_sio):
        if row[0] in seen:
            continue  # skip duplicate
        new_sio.write(row)
    csv = new_sio.getvalue()
    return csv


def get_column_mapping(list_type_id=None):
    """
    Returns the column mapping dict for posting a CSV list to SmartFocus' API.

    Args:
        list_type_id: Type of list
    Returns:
        Dict of ordered column mappings
    Raises:
        Exception
    """
    mappings = [
        {"1": "EMAIL",  # Default
         "2": "CUSTNUM",
         "3": "FIRSTNAME",
         "4": "LASTNAME"},
        {"1": "EMAIL",  # Entire House File + Autoship
         "2": "CUSTNUM",
         "3": "FIRSTNAME",
         "4": "LASTNAME"},
        {"1": "EMAIL",  # Entire House File - Autoship
         "2": "CUSTNUM",
         "3": "FIRSTNAME",
         "4": "LASTNAME"},
        {"1": "EMAIL",  # Re-engagement Files
         "2": "CUSTNUM",
         "3": "FIRSTNAME",
         "4": "LASTNAME",
         "5": "ACTIVE"},
        {"1": "EMAIL",  # Autoship Only
         "2": "CUSTNUM",
         "3": "FIRSTNAME",
         "4": "LASTNAME"},
        {"1": "EMAIL",  # Category Cross-Sell
         "2": "CUSTNUM",
         "3": "FIRSTNAME",
         "4": "LASTNAME",
         "5": "LISTNAME"},
        {"1": "EMAIL",  # By Product Purchased (time to reorder)
         "2": "CUSTNUM",
         "3": "FIRSTNAME",
         "4": "LASTNAME",
         "5": "LISTNAME"}
    ]

    if list_type_id is None:
        return mappings[0]
    else:
        return mappings[list_type_id]
