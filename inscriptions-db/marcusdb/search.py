
from flask import render_template, current_app, request, jsonify
import pysolr

# Number of items per page
ITEMS_PER_PAGE = 10
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
        'start': start,
        'rows': ITEMS_PER_PAGE
    })

    # Calculate the total number of pages
    total_results = results.hits
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

    # GET all filters values
    filters = getAllFilters(solr)

    # results = solr.search('*',rows=3000)
    return render_template('results.html', res=list(results), filters=filters, page=page, total_pages=total_pages, page_numbers=page_numbers)

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
def getAllFilters(solr):
    regions = getAllRowsByField(solr, 'region')
    activities = getAllRowsByField(solr, 'activity')
    authorities = getAllRowsByField(solr, 'authority')
    purposes = getAllRowsByField(solr, 'purpose')
    contextes = getAllRowsByField(solr, 'context')
    lines = getAllRowsByField(solr, 'lines')
    materials = getAllRowsByField(solr, 'material')
    natures = getAllRowsByField(solr, 'nature')
    denominations = getAllRowsByField(solr, 'denomination')

    filters = {
        'regions': {hits: region for hits, region in regions},
        'activities': {hits: activity for hits, activity in activities},
        'authorities': {hits: auth for hits, auth in authorities},
        'purposes': {hits: purpose for hits, purpose in purposes},
        'contextes': {hits: context for hits, context in contextes},
        'lines': {hits: line for hits, line in lines},
        'materials': {hits: material for hits, material in materials},
        'natures': {hits: nature for hits, nature in natures},
        'denominations': {hits: denomination for hits, denomination in denominations}
    }

    return filters
    
def getAllRowsByField(solr, field):
    results = solr.search('*:*', **{
        'facet': 'true',
        'facet.field': field,
        # 'facet.limit': -1,  # Set to -1 to get all distinct values
        'rows': 0
    })

    distinct_values = results.facets['facet_fields'][field]
    # The facets are returned as a list with alternating values and counts
    values_with_hits = [(distinct_values[i+1], distinct_values[i])
                        for i in range(0, len(distinct_values), 2)]

    return values_with_hits

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