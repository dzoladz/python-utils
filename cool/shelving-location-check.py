#!/home/derekz/cool/bin/python
# Consortium of Ohio Libaries
#
#
# Description: Report if an item does not have a shelving location set
# Notes: Output files will be in .xls format
#
###############################################
# SET SCRIPT VARIABLES & DEFINE SQL QUERY BELOW
output_filename = 'shelving-location'
email_message = 'Attached is the quarterly shelving location report. Check these items to ensure that a shelving location has been assigned. At checkout, shelving location is one factor used by Evergreen to determine which circulation policy should be applied to a transaction. If no shelving location is assigned to an item, an unexpected circulation policy may be applied to the transaction'
email_subject = '[SuperCats] Quarterly: Shelving Location Report'
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

# ------------------------------------
# If successful connection, run query
# ------------------------------------

rows = db.query("""\
SELECT ou.name AS "Library",
	b.id AS "TCN",
    cn.label AS "Call Number",
    c.barcode AS "Barcode",
    ARRAY_TO_STRING(
    XPATH('//m:datafield[@tag="245"]/m:subfield[@code="a"]/text()', b.marc::xml, ARRAY[ARRAY['m','http://www.loc.gov/MARC21/slim']]), ' ') AS "Title",
    'Copy Location ''Stacks'' is undefined' AS "Issue"
FROM biblio.record_entry b
    INNER JOIN asset.call_number cn ON cn.record=b.id
    INNER JOIN asset.copy c ON c.call_number=cn.id
    INNER JOIN actor.org_unit ou on ou.id=c.circ_lib
WHERE b.deleted=FALSE
    AND c.deleted=FALSE
    AND b.id != -1
    AND c.location = 1 -- i.e. Stacks
ORDER BY ou.name, c.barcode;
""")

# --------------------------------
# Write Query Results to .xls File
# --------------------------------
# Add extension, open file and write
outfile = output_filename + '.xls'
with open(outfile, 'wb') as file:
        file.write(rows.export('xls'))

# -----------------
# Email .xls Report
# -----------------
# Add required double-quotes and send
email_message = '"{}"'.format(email_message)
email_subject = '"{}"'.format(email_subject)
subprocess.call('echo ' + email_message + ' | mail -b ' + email_bcc + ' -a ' + outfile + ' -s ' + email_subject + ' ' + email_to + '; sleep 10; rm ' + outfile, shell=True)
