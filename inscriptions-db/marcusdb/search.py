
from flask import render_template, current_app, request, jsonify, Response
import pysolr

# Number of items per page
ITEMS_PER_PAGE = 100
TOKEN = 'pk.eyJ1IjoiaW1yYW5hc2lmIiwiYSI6ImNseDBjaTNtbTA1dDcyaXNjdjJsa2tlbWIifQ.2_kCycbjY-7_LrlucTewZw'

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