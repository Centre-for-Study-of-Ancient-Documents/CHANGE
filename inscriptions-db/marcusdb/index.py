
import csv
import sys
import re
from xml.sax.saxutils import escape

# id
# _region_
# city
# location
# reference
# reference_num
# bib_url
# date_from
# date_to
# description
# phi_url
# phi_id
# doc_type
# authority
# activity
# purpose
# context
# denomination
# notes

REGION="REGION"
CITY="CITY"
PLACE_OF_PUBLICATION = "PLACE OF PUBLICATION"
LAT="LATITUDE"
LONG="LONGITUDE"
REF="REFERENCE"
REF_NUM="REFERENCE NUMBER"
BIB_URL="BIBLIOGRAPHIC URL"
REF2="REFERENCE 2"
REF3="REFERENCE 3"
DATE="DATE"
DATE_CERT="DATE CERTAINTY"
DATE_FROM="DATE FROM"
DATE_TO="DATE TO"
DESC="DESCRIPTION"
PHI_URL="PHI URL"
PHI_ID="PHI ID"
TRIS_ID="TRISMEGISTOS ID"
DOC_TYPE="DOCUMENT TYPE"
AUTHORITY="AUTHORITY"
ACTIVITY="ACTIVITY"
PURPOSE="PURPOSE/FOCUS"
CONTEXT="CONTEXT/FIELD OF ACTION"
LINES="LINES"
MATERIAL="MATERIAL"
NATURE="NATURE"
DENOM="DENOMINATION"
NOTES="NOTES"

activity_fields = { ACTIVITY, AUTHORITY, PURPOSE, CONTEXT, LINES, MATERIAL,
                    NATURE, DENOM, NOTES }

solr_fields = {
        # id
        # location
        "region":REGION,
        "city":CITY,
        "place_of_publication": PLACE_OF_PUBLICATION,
        "lat": LAT,
        "long": LONG,
        "reference":REF,
        "reference_num":REF_NUM,
        "bib_url":BIB_URL,
        "date_from":DATE_FROM,
        "date_to":DATE_TO,
        "description":DESC,
        "phi_url":PHI_URL,
        "phi_id":PHI_ID,
        "doc_type":DOC_TYPE,
        "authority":AUTHORITY,
        "activity":ACTIVITY,
        "purpose":PURPOSE,
        "context":CONTEXT,
        "lines":LINES,
        "material":MATERIAL,
        "nature":NATURE,
        "denomination":DENOM,
        "notes":NOTES
    }

processed = 0
ln = 0
sectionId = ''
stored = {}
docs = []

# Print to stderr
def printe(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def fix_region(region):
    """Fix region names which also have descriptions in parens"""
    return re.sub(' *\(.*\)', '', region)

def mkdoc(l, s):
    out = " <doc>\n"
    out += '  <field name="id">item-' + sectionId + '.' + str(ln) + '</field>\n'
    for sf in solr_fields:
        f = solr_fields[sf]
        if f in activity_fields:
            val = l[f]
        else:
            val = s[f]
        out += '  <field name="' + sf + '">' + str(escape(val)) +'</field>\n' 
    out += " </doc>\n"
    return out

def process_entry(l):
    global processed, stored, docs
    if l[REGION]:
        stored[REGION] = fix_region(l[REGION])
        #print(stored[REGION])
        # Ignore other cells on region line
        return
    if l[CITY]:
        stored[CITY] = l[CITY]
        stored[PLACE_OF_PUBLICATION] = str(l[PLACE_OF_PUBLICATION])
        stored[LAT] = str(l[LAT])
        stored[LONG] = str(l[LONG])
        printe(stored[REGION], stored[CITY], stored[PLACE_OF_PUBLICATION], stored[LAT], stored[LONG], ln)
    if l[REF]:
        stored[REF] = l[REF]
        stored[REF_NUM] = l[REF_NUM]
        stored[BIB_URL] = l[BIB_URL]
        stored[PHI_ID] = l[PHI_ID]
        stored[PHI_URL] = l[PHI_URL]
        stored[TRIS_ID] = l[TRIS_ID]
        stored[DATE] = l[DATE]
        stored[DATE_CERT] = l[DATE_CERT]
        stored[DATE_FROM] = l[DATE_FROM]
        stored[DATE_TO] = l[DATE_TO]
        stored[DESC] = l[DESC]
        stored[DOC_TYPE] = l[DOC_TYPE]
        #print(ln, l[PURPOSE])
        docs.append(mkdoc(l, stored))
        processed += 1
    else:
        if any(l[x] for x in activity_fields):
            #printe(ln, l[PURPOSE])
            docs.append(mkdoc(l, stored))
            processed += 1

    return

def index_csv(filename, section):
    global processed, ln, sectionId
    printe("File to index: "+filename)

    sectionId = section

    with open(filename, 'r', encoding='utf-8-sig') as infile:
        lines = csv.DictReader(infile)

        total = 0
        ln = 1
        for l in lines:
            ln += 1
            #printe("line:",ln)
            #printe(l)
            process_entry(l)
            if processed >=200:
                printe("count:",processed , total)
                total += processed
                processed = 0
            #city=(r["CITY"])
            #break
        total += processed
        printe("count:",processed, total)

        sys.stdout.write('<add>\n')
        sys.stdout.write(''.join(docs))
        sys.stdout.write('</add>')

        printe("Done")

