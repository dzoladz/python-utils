#!/home/derekz/cool/bin/python
# Consortium of Ohio Libaries
#
#
# Description: Report to check for items attached to Ohio Digital Library records
# Notes: Output will be in the email body
#
###############################################
# SET SCRIPT VARIABLES & DEFINE SQL QUERY BELOW
email_message = 'Below are the results of the monthly Ohio Digital Library attached items report. This report identifies the TCN of Ohio Digital Library records that have item records attached to them in error. The item needs to be moved to the proper bibliographic record or a new bibliographic record needs to be created for the item.'
email_subject = '[SuperCats] Monthly: Ohio Digital Library, Items Attached Report'
email_to = 'derek@example.org'
email_bcc = 'derek@example.org'
###############################################

import psycopg2
import records
import credentials
import subprocess

# --------------------------------------------------
# Connect to COOL's production database as read-only
# --------------------------------------------------
try:
    # Grab database credentials
    user = credentials.login_full['user']
    password = credentials.login_full['password']
    host = credentials.login_full['host']
    port = credentials.login_full['port']
    dbname = credentials.login_full['dbname']

    # Create db connection
    connect = 'postgres://' + user + ':' + password + '@' + host + ':' + port + '/' + dbname

    # Try to connect to db
    db = records.Database(connect)

except Exception as e:
    print("Cannot connect to the database")
    print(e)

# -------------------------------------
# If successful connection, run queries
# -------------------------------------

ohia = db.query("""\
SELECT
bre.tcn_value AS "TCN",
rmsr.title AS "Title"
FROM asset.copy acopy
LEFT OUTER JOIN asset.call_number acall ON (acopy.call_number = acall.id)
LEFT OUTER JOIN biblio.record_entry bre1 ON (acall.record = bre1.id)
LEFT OUTER JOIN reporter.materialized_simple_record rmsr ON (bre1.id = rmsr.id)
LEFT OUTER JOIN metabib.full_rec mbfr ON (bre1.id = mbfr.record)
LEFT OUTER JOIN biblio.record_entry bre ON (mbfr.record = bre.id)
  WHERE ((mbfr.tag) IS NULL OR mbfr.tag = '049')
AND ((mbfr.value) IS NULL OR mbfr.value = 'ohia')
AND ((mbfr.subfield) IS NULL OR mbfr.subfield = 'a')
AND acopy.deleted = 'f'
GROUP BY 1, 2
ORDER BY bre.tcn_value ASC, rmsr.title ASC;
""")

srba = db.query("""\
SELECT
bre.tcn_value AS "TCN",
rmsr.title AS "Title"
FROM asset.copy acopy
LEFT OUTER JOIN asset.call_number acall ON (acopy.call_number = acall.id)
LEFT OUTER JOIN biblio.record_entry bre1 ON (acall.record = bre1.id)
LEFT OUTER JOIN reporter.materialized_simple_record rmsr ON (bre1.id = rmsr.id)
LEFT OUTER JOIN metabib.full_rec mbfr ON (bre1.id = mbfr.record)
LEFT OUTER JOIN biblio.record_entry bre ON (mbfr.record = bre.id)
  WHERE ((mbfr.tag) IS NULL OR mbfr.tag = '049')
AND ((mbfr.value) IS NULL OR mbfr.value = 'srba')
AND ((mbfr.subfield) IS NULL OR mbfr.subfield = 'a')
AND acopy.deleted = 'f'
GROUP BY 1, 2
ORDER BY bre.tcn_value ASC, rmsr.title ASC;
""")


# --------------------------------
# Construct the Email Body
# --------------------------------

ohia = ohia.dataset
srba = srba.dataset
results = email_message + str(srba) + '\n\n' + str(ohia)

# -----------------
# Email .xls Report
# -----------------
# Add required double-quotes and send
email_message = '"{}"'.format(email_message)
email_subject = '"{}"'.format(email_subject)
results = '"{}"'.format(results)
subprocess.call('echo ' + results  + ' | mail -b ' + email_bcc + ' -s ' + email_subject + ' ' + email_to + ';', shell=True)
