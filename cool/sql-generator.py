# SQL GENERATOR
# Process a .csv file to generate SQL
#
#!/usr/local/bin/python3

import csv, argparse

# Establish command line values
parser = argparse.ArgumentParser(description='Read an CVS Input File to Generate SQL to Remove Patron Alert Message')
parser.add_argument('--infile', '-i', type=str, required=True, help='Path to the .csv file')
parser.add_argument("--outfile", "-o", type=str, required=True, help='Path for the output file of generated SQL')
args = parser.parse_args()

# Open output file set with command line arg
outfile = open(args.outfile, 'w')

# Begin Transaction Block
outfile.write("Begin;" + '\n')

# Iterate through the .cvs input file set with command line arg, write SQL
with open(args.infile, newline='') as inputfile:
    rows = csv.reader(inputfile)
    next(rows) # remove header row
    for row in rows:
        outfile.write("UPDATE asset.copy_note SET pub = 'f', title = '', value = '' WHERE id =  '" + row[0].strip() + "';" + '\n')

## Close the file
outfile.close()