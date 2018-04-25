#!/home/derekz/cool/bin/python
# Consortium of Ohio Libaries
#
#
# Description: Report on imported Ohio Digital Library records
# Notes: Output will be in the email body
#
###############################################
# SET SCRIPT VARIABLES & DEFINE SQL QUERY BELOW
email_message = 'Below are the results of the monthly Ohio Digital Library report. This report identifies TCNs for Ohio Digital Library records that do not have their bibliographic source set to Ohio Digital Library. Bib Source is used by Evergreen to control the visibility of records in the public OPAL. The Ohio Digital Library bib source instructs Evergreen to use the 856 \$9 values to expose these records in local catalog searches'
email_subject = 'Monthly: Ohio Digital Library Report'
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

tcns = db.query("""\
SELECT
	bre.tcn_value AS "Check the bib source on the following TCNs"
FROM biblio.record_entry bre
	INNER JOIN metabib.real_full_rec mrfr ON (bre.id = mrfr.record)
WHERE (bre.source != '101' OR bre.source is null)
	AND (bre.create_date BETWEEN date_trunc('month', now()) - interval '3 month'
		AND date_trunc('month', now()))
	AND mrfr.tag = '856'
	AND mrfr.value like '%overdrive%'
	AND deleted IS FALSE
ORDER BY bre.create_date DESC;
""")

counts = db.query("""\
SELECT
	count(bre.tcn_value) AS "Count of previous month's imports"
FROM biblio.record_entry bre
	INNER JOIN metabib.real_full_rec mrfr ON (bre.id = mrfr.record)
WHERE (bre.source = '101')
	AND (bre.create_date BETWEEN date_trunc('month', now()) - interval '3 month'
		AND date_trunc('month', now()))
	AND mrfr.tag = '856'
	AND mrfr.value like '%overdrive%'
	AND deleted IS FALSE;
""")

# --------------------------------
# Construct the Email Body
# --------------------------------

tcns = tcns.dataset
counts = counts.dataset
results = email_message + '\n\n' + str(tcns) + '\n\n' + str(counts)

# -----------------
# Email .xls Report
# -----------------
# Add required double-quotes and send
email_message = '"{}"'.format(email_message)
email_subject = '"{}"'.format(email_subject)
results = '"{}"'.format(results)
subprocess.call('echo ' + results  + ' | mail -b ' + email_bcc + ' -s ' + email_subject + ' ' + email_to + ';', shell=True)
