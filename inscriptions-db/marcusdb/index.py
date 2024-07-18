
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
PLACE_OF_CONCEPTION = "PLACE OF CONCEPTION"
PLACE_OF_TRANSACTION = "PLACE OF TRANSACTION"
LAT="LATITUDE"
LONG="LONGITUDE"
REF="REFERENCE"
REF_NUM="REFERENCE NUMBER"
BIB_URL="BIBLIOGRAPHIC URL"
REF_2="REFERENCE 2"
REF_NUM_2="REFERENCE NUMBER 2"
REF_3="REFERENCE 3"
REF_NUM_3="REFERENCE NUMBER 3"
DATE="DATE"
DATE_CERT="DATE CERTAINTY"
DATE_FROM="DATE FROM"
DATE_TO="DATE TO"
DESC="DESCRIPTION"
PHI_URL="PHI URL"
PHI_URL_2="PHI URL 2"
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
COMBINED_REF = "COMBINED_REF"
COMBINED_REF_2 = "COMBINED_REF_2"
COMBINED_REF_3 = "COMBINED_REF_3"

activity_fields = { ACTIVITY, AUTHORITY, PURPOSE, CONTEXT, LINES, MATERIAL,
                    NATURE, DENOM, NOTES }

solr_fields = {
        # id
        # location
        "region":REGION,
        "city":CITY,
        "place_of_publication": PLACE_OF_PUBLICATION,
        "place_of_conception": PLACE_OF_CONCEPTION,
        "place_of_transaction": PLACE_OF_TRANSACTION,
        "lat": LAT,
        "long": LONG,
        "reference":REF,
        "reference_num":REF_NUM,
        "reference_2":REF_2,
        "reference_num_2":REF_NUM_2,
        "reference_3":REF_3,
        "reference_num_3":REF_NUM_3,
        "bib_url":BIB_URL,
        "date_from":DATE_FROM,
        "date_to":DATE_TO,
        "description":DESC,
        "phi_url":PHI_URL,
        "phi_url_2":PHI_URL_2,
        "phi_id":PHI_ID,
        "tm_id":TRIS_ID,
        "doc_type":DOC_TYPE,
        "authority":AUTHORITY,
        "activity":ACTIVITY,
        "purpose":PURPOSE,
        "context":CONTEXT,
        "lines":LINES,
        "material":MATERIAL,
        "nature":NATURE,
        "denomination":DENOM,
        "notes":NOTES,
        "epigraphic_reference": COMBINED_REF,
        "epigraphic_reference_2": COMBINED_REF_2,
        "epigraphic_reference_3": COMBINED_REF_3
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
            out += '  <field name="' + sf + '">' + str(escape(val)) +'</field>\n' 
        else:
            if f in s:
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
        stored[COMBINED_REF] = l[REF] + ' ' + l[REF_NUM]
        stored[BIB_URL] = l[BIB_URL]
        stored[PHI_ID] = l[PHI_ID]
        stored[PHI_URL] = l[PHI_URL]

        if l[PLACE_OF_CONCEPTION]:
            stored[PLACE_OF_CONCEPTION] = str(l[PLACE_OF_CONCEPTION])
        if l[PLACE_OF_TRANSACTION]:    
            stored[PLACE_OF_TRANSACTION] = str(l[PLACE_OF_TRANSACTION])

        if l[PHI_URL_2]:
            stored[PHI_URL_2] = str(l[PHI_URL_2])

        stored[TRIS_ID] = l[TRIS_ID]
        stored[DATE] = l[DATE]
        stored[DATE_CERT] = l[DATE_CERT]
        stored[DATE_FROM] = l[DATE_FROM]
        stored[DATE_TO] = l[DATE_TO]
        stored[DESC] = l[DESC]
        stored[DOC_TYPE] = l[DOC_TYPE]
        
        if l[REF_2]:
            stored[REF_2] = l[REF_2]
            stored[REF_NUM_2] = l[REF_NUM_2]
            stored[COMBINED_REF_2] = l[REF_2] + ' ' + l[REF_NUM_2]

        if l[REF_3]:
            stored[REF_3] = l[REF_3]
            stored[REF_NUM_3] = l[REF_NUM_3]
            stored[COMBINED_REF_3] = l[REF_3] + ' ' + l[REF_NUM_3]

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

