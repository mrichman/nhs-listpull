import csv
import logging
from io import BytesIO, StringIO


def extract_emails_from_csv(csv_data):
    """
    Given CSV formatted input, return a list of all email addresses. This
    function assumes emails are in the first column.
    :type csv_data: str or unicode
    """
    emails = []
    f = StringIO(csv_data)
    for row in csv.reader(f, delimiter=','):
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
        for row in csv.reader(csv_data):
            if row[0] not in emails:
                # Write to new csv
                csv.writer(bio).writerow([unicode(s).encode() for s in row])
                count += 1
    except UnicodeEncodeError as uee:
        logging.error(uee)
        raise
    except Exception as ex:
        logging.error(ex.message)
        raise
    return bio.getvalue()
