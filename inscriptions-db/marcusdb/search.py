
from flask import render_template, current_app, request, jsonify, Response
import pysolr
import csv
import io

# Number of items per page
ITEMS_PER_PAGE = 10
TOKEN = 'pk.eyJ1IjoiaW1yYW5hc2lmIiwiYSI6ImNseDBjaTNtbTA1dDcyaXNjdjJsa2tlbWIifQ.2_kCycbjY-7_LrlucTewZw'

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


def results():
    corename = current_app.config["SOLR_CORE"]

    solr = pysolr.Solr(corename)
    # results = solr.search('city:Sardis')

    # Get the search query from the request parameters
    search_query = buildSearchQuery(request)

    # Get the current page number from the query parameters, default to 1
    page = request.args.get('page', 1, type=int)

    # Calculate the start index for the current page
    start = (page - 1) * ITEMS_PER_PAGE

    print(search_query)

    # Perform the Solr query with pagination parameters
    results = solr.search(search_query, **{
        'group': 'true',                 # Enable grouping
        'group.field': 'inscription',      # Group by the specified field
        'group.ngroups': 'true',         # Return the number of groups
        'group.limit': 1,                # Limit the number of documents per group
        'start': start,
        'rows': ITEMS_PER_PAGE,
        #'sort': ''
    })

    #distinct_results = list({item['inscription']: item for item in list(results)}.values())

    # Calculate the total number of pages
    total_results = results.raw_response['grouped']['inscription']['ngroups']
    groups = results.raw_response['grouped']['inscription']['groups']

    total_pages = (total_results + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    # Generate page range
    if total_pages <= 10:
        page_numbers = range(1, total_pages + 1)
    else:
        if page <= 6:
            page_numbers = list(range(1, 8)) + ['...', total_pages]
        elif page > total_pages - 6:
            page_numbers = [1, '...'] + \
                list(range(total_pages - 6, total_pages + 1))
        else:
            page_numbers = [1, '...'] + \
                list(range(page - 2, page + 3)) + ['...', total_pages]

    # Extract the docs from each group
    docs = [group['doclist']['docs'][0] for group in groups]

    # GET all filters values
    filters = getAllFilters(solr, search_query, total_results)

    # results = solr.search('*',rows=3000)
    return render_template('results.html', res=docs, filters=filters, page=page, total_pages=total_pages, page_numbers=page_numbers)

def buildSearchQuery(request):
    search_query = request.args.get('q', '*:*')

    # make filter query
    filter_query = ''
    for arg in request.args:
        if arg != 'q' and arg != 'page' and arg != 'operator' and arg != 'date_from' and arg != 'date_to':
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

# ===================================================================================================
# Get Full Text query
def fullTextQuery(txt):
    print('Full TEXT search ==========')
    return f"(description:(+'{txt}') OR notes:(+'{txt}'))"

# ====================================================================================================
# Filters
def getAllFilters(solr, search_query, total_results):
    # 1regions = getAllRowsByField(solr, 'region', search_query)
    # cities = getAllRowsByField(solr, 'city', search_query)
    # docTypes = getAllRowsByField(solr, 'doc_type', search_query)
    # epigraphic_references = getAllRowsByField(solr, 'epigraphic_reference', search_query)
    # activities = getAllRowsByField(solr, 'activity', search_query)
    # authorities = getAllRowsByField(solr, 'authority', search_query)
    # purposes = getAllRowsByField(solr, 'purpose', search_query)
    # contextes = getAllRowsByField(solr, 'context', search_query)
    # lines = getAllRowsByField(solr, 'lines', search_query)
    # materials = getAllRowsByField(solr, 'material', search_query)
    # natures = getAllRowsByField(solr, 'nature', search_query)
    # denominations = getAllRowsByField(solr, 'denomination', search_query)
    # dateCertains = getAllRowsByField(solr, 'date_cert', search_query)

    facet_fields = ['region', 'city', 'doc_type', 'epigraphic_reference', 
                'activity', 'authority', 'purpose', 'context', 
                'lines', 'material', 'nature', 'denomination', 'date_cert']

    all_facets = getAllRowsByField(solr, facet_fields, search_query)

    #print("**** epigraphic_references: " )
    ##print(len(epigraphic_references))
    #print(epigraphic_references)

    filters = {
        'regions': all_facets['region'],
        'cities': all_facets['city'],
        'epigraphic_references': all_facets['epigraphic_reference'],
        'docTypes': all_facets['doc_type'],
        'activities': all_facets['activity'],
        'authorities': all_facets['authority'],
        'purposes': all_facets['purpose'],
        'contextes': all_facets['context'],
        'lines': all_facets['lines'],
        'materials': all_facets['material'],
        'natures': all_facets['nature'],
        'denominations': all_facets['denomination'],
        'dateCertains': all_facets['date_cert']
    }

    return filters
    #print(all_facets)
    #return all_facets
    
def getAllRowsByField(solr, fields, search_query):
    results = solr.search(search_query, **{
        'facet': 'true',
        'facet.field': fields,
        'facet.limit': -1,  # Set to -1 to get all distinct values
        'facet.sort': 'count',
        'rows': 0
    })

    #distinct_values = results.facets['facet_fields'][field]
    facets = {field: results.facets['facet_fields'][field] for field in fields}


    # The facets are returned as a list with alternating values and counts
    #values_with_hits = [(distinct_values[i+1], distinct_values[i])
    #                    for i in range(0, len(distinct_values), 2)]

    return facets

# ====================================================================================================
# Lat lng
def getAllLatLang():
    corename = current_app.config["SOLR_CORE"]
    solr = pysolr.Solr(corename)

    # Get the search query from the request parameters
    search_query = buildSearchQuery(request)

    results = solr.search(search_query, **{
        'rows': 0
    })

    print('from API query ', search_query)

    mapRes = solr.search(search_query, **{
        'rows': results.hits
    })

    #print('Map: ', list(mapRes)[0]['lat'], ' Hits: ', mapRes.hits, ' Results:', results.hits)
    return jsonify({ 'mapResults': list(mapRes), 'mapbox_token': TOKEN })