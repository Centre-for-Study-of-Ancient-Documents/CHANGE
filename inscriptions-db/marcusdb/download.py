from flask import render_template, current_app, request, jsonify, Response
import pysolr
import csv
import io
from io import BytesIO
import pandas as pd
import json
import xml.etree.ElementTree as ET

REGION="REGION"
CITY="CITY"
PLACE_OF_PUBLICATION = "PLACE OF PUBLICATION"
PLACE_OF_CONCEPTION = "PLACE OF CONCEPTION"
PLACE_OF_TRANSACTION = "PLACE OF TRANSACTION"
LAT="LATITUDE"
LONG="LONGITUDE"
REGION_SPECIFIED="REGION SPECIFIED"
MISCELLANEOUS_NOTES_ON_EDITIONS = "MISCELLANEOUS NOTES ON EDITIONS"
MULTIPLES="MULTIPLES"
DUPLICATES="DUPLICATES"
REFERENCE_IN_FULL="REFERENCE IN FULL"
REF="REFERENCE"
REF_NUM="REFERENCE NUMBER"
BIB_URL="BIBLIOGRAPHIC URL"
BIB_URL_2="BIBLIOGRAPHIC URL 2"
BIB_URL_3="BIBLIOGRAPHIC URL 3"
REF_2="REFERENCE 2"
REF_NUM_2="REFERENCE NUMBER 2"
REF_3="REFERENCE 3"
REF_NUM_3="REFERENCE NUMBER 3"
DATE="DATE"
DATE_CERT="DATE CERTAINTY"
DATE_FROM="DATE FROM"
DATE_TO="DATE TO"
DESC="DESCRIPTION"
NOTES_ON_THE_MONUMENT_FINDSPOT="NOTES ON THE MONUMENT/FINDSPOT"
PHI_URL="PHI URL"
PHI_URL_2="PHI URL 2"
PHI_ID="PHI ID"
TRIS_ID="TRISMEGISTOS ID"
NON_PHI_URL = "NON-PHI URL"
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

solr_fields = {
        "region":REGION,
        "city":CITY,
        "place_of_publication": PLACE_OF_PUBLICATION,
        "place_of_conception": PLACE_OF_CONCEPTION,
        "place_of_transaction": PLACE_OF_TRANSACTION,
        "lat": LAT,
        "long": LONG,
        "region_specified": REGION_SPECIFIED,
        "miscellaneous_notes_on_editions": MISCELLANEOUS_NOTES_ON_EDITIONS,
        "multiples": MULTIPLES,
        "duplicates":DUPLICATES,
        "reference_in_full": REFERENCE_IN_FULL,
        "reference":REF,
        "reference_num":REF_NUM,
        "bib_url":BIB_URL,
        "reference_2":REF_2,
        "reference_num_2":REF_NUM_2,
        "bib_url_2":BIB_URL_2,
        "reference_3":REF_3,
        "reference_num_3":REF_NUM_3,
        "bib_url_3":BIB_URL_3,
        "date": DATE,
        "date_cert": DATE_CERT,
        "date_from":DATE_FROM,
        "date_to":DATE_TO,
        "description":DESC,
        "notes_on_the_monument_findspot": NOTES_ON_THE_MONUMENT_FINDSPOT,
        "phi_url":PHI_URL,
        "phi_url_2":PHI_URL_2,
        "phi_id":PHI_ID,
        "tm_id":TRIS_ID,
        "non_phi_url": NON_PHI_URL,
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
    }

def buildSearchQuery(request):
    search_query = request.args.get('q', '*:*')

    # make filter query
    filter_query = ''
    for arg in request.args:
        if arg != 'q' and arg != 'page' and arg != 'operator' and arg != 'date_from' and arg != 'date_to' and arg != 'rdoDateOption':
            if (filter_query != ''):
                filter_query = f'{filter_query} {request.args.get("operator")} '

            values = [
                f'{arg}:"{value}"' for value in request.args.getlist(arg) if value]
            if (len(values) > 0):
                filter_query += ' (' + ' OR '.join(values) + ')'

        # filter_query = filter_query + ' (' + ' OR '.join([f'{arg}:"{value}"' for value in request.args.getlist(arg) if value]) + ')'

    # date filter
    date_filter = ''
    if request.args.get("date_from") and request.args.get("date_to"):
        if(request.args.get('rdoDateOption')):
            date_filter = f' (date_from:[{request.args.get("date_from")} TO {request.args.get("date_to")}] AND date_to:[{request.args.get("date_from")} TO {request.args.get("date_to")}]) '
        else:
            date_filter = f' (date_from:[* TO {request.args.get("date_from")}] AND date_to:[{request.args.get("date_to")} TO *]) '
    elif request.args.get("date_from"):
        date_filter = f' date_from:[* TO {request.args.get("date_from")}] '
    elif request.args.get("date_to"):
        date_filter = f' date_to:[{request.args.get("date_to")} TO *] '

    if date_filter != '' and filter_query != '':
        filter_query += f'{request.args.get("operator")} {date_filter}'
    else:
        filter_query += f'{date_filter}'

    if search_query == '' or search_query == '*:*':
        search_query = '*:*'
    else:
        search_query = fullTextQuery(search_query)

    if filter_query != '' and search_query != '*:*':
        search_query = f'{search_query} {request.args.get("operator")} {filter_query}'
    elif filter_query != '':
        search_query = filter_query
    
    return search_query 

# Get Full Text query
def fullTextQuery(txt):
    print('Full TEXT search ==========')
    return f"(description:(+'{txt}') OR notes:(+'{txt}'))"


def downloadCSV():
    corename = current_app.config["SOLR_CORE"]

    solr = pysolr.Solr(corename)
    # results = solr.search('city:Sardis')

    # Get the search query from the request parameters
    search_query = buildSearchQuery(request)

    print('Download CSV: ', search_query)

    # Perform the Solr query with pagination parameters
    results = solr.search(search_query, **{
       'rows': 0
    })

    # Calculate the total number of pages
    total_results = results.hits

    # Perform the Solr query with pagination parameters
    results = solr.search(search_query, **{
        'rows': total_results,
        'sort': ''
    })

    output = io.StringIO()
    writer = csv.writer(output)
    
    if results.docs:
        writer.writerow(solr_fields.values())  # Write the headers from the first document
    
    for doc in results.docs:
        row = [doc.get(key, "") for key in solr_fields]
        writer.writerow(row)

    output.seek(0)
    
    response = Response(output, mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename='results.csv')
    return response

def downloadExcel():
    corename = current_app.config["SOLR_CORE"]

    solr = pysolr.Solr(corename)
    # results = solr.search('city:Sardis')

    # Get the search query from the request parameters
    search_query = buildSearchQuery(request)

    print('Download Excel: ', search_query)

    # Perform the Solr query with pagination parameters
    results = solr.search(search_query, **{
       'rows': 0
    })

    # Calculate the total number of pages
    total_results = results.hits

    # Perform the Solr query with pagination parameters
    results = solr.search(search_query, **{
        'rows': total_results,
        'sort': ''
    })

    # Step 2: Extract all fields dynamically from Solr results
    data = []
   
    #data.append(solr_fields.values())

    if results.docs:
        for doc in results.docs:
            row = [doc.get(key, "") for key in solr_fields]
       #for result in results:
            data.append(row)
    
    # Step 3: Convert the data to a pandas DataFrame
    df = pd.DataFrame(data, columns=solr_fields.values())

     # Reset index to ensure no index is written
    df.reset_index(drop=True)

    # Step 4: Create an in-memory Excel file
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    # Step 5: Rewind the buffer
    output.seek(0)
    
    # Step 6: Create the response and set headers
    response = Response(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers.set('Content-Disposition', 'attachment', filename='results.xlsx')

    return response


def downloadXML():
    corename = current_app.config["SOLR_CORE"]

    solr = pysolr.Solr(corename)
    # results = solr.search('city:Sardis')

    # Get the search query from the request parameters
    search_query = buildSearchQuery(request)

    print('Download XML: ', search_query)

    # Perform the Solr query with pagination parameters
    results = solr.search(search_query, **{
       'rows': 0
    })

    # Calculate the total number of pages
    total_results = results.hits

    # Perform the Solr query with pagination parameters
    results = solr.search(search_query, **{
        'rows': total_results,
        'sort': ''
    })

   # Step 2: Create the root element for the XML file
    root = ET.Element("Documents")

    # Step 3: Dynamically build the XML structure from Solr results
    for result in results:
        doc_elem = ET.SubElement(root, "Document")
        for key, value in result.items():
            field_elem = ET.SubElement(doc_elem, key)
            field_elem.text = str(value)

    # Step 4: Convert the XML tree into a string
    # tree = ET.ElementTree(root)
    # output = BytesIO()
    # #output = io.StringIO()
    # tree.write(output, encoding='utf-8', xml_declaration=True)
    # output.seek(0)

    # Step 2: Convert the XML tree into a string
    xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')

    # Step 6: Create the response and set headers
    response = Response(xml_string, mimetype='application/xml')
    response.headers.set('Content-Disposition', 'attachment', filename='results.xml')

    return response

def downloadJSON():
    corename = current_app.config["SOLR_CORE"]

    solr = pysolr.Solr(corename)
    # results = solr.search('city:Sardis')

    # Get the search query from the request parameters
    search_query = buildSearchQuery(request)

    print('Download JSON: ', search_query)

    # Perform the Solr query with pagination parameters
    results = solr.search(search_query, **{
       'rows': 0
    })

    # Calculate the total number of pages
    total_results = results.hits

    # Perform the Solr query with pagination parameters
    results = solr.search(search_query, **{
        'rows': total_results,
        'sort': ''
    })

    # Step 2: Extract all fields dynamically from Solr results
    data = []
    
    for result in results:
        data.append(result)

    # Step 3: Convert the data to JSON
    json_data = json.dumps(data)
    
    # Step 4: Create the response for JSON download
    response = Response(json_data, mimetype='application/json')
    response.headers.set('Content-Disposition', 'attachment', filename='results.json')

    return response    
