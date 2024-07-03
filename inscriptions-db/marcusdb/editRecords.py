
from flask import render_template, current_app, request, jsonify
import pysolr

# ====================================================================================================
# Lat lng
def results():
    corename = current_app.config["SOLR_CORE"]
    solr = pysolr.Solr(corename)

    # Get the search query from the request parameters
    search_query = '*:*'

    results = solr.search(search_query, **{
        'rows': 0
    })

    mapRes = solr.search(search_query, **{
        'rows': results.hits
    })

    #print('Map: ', list(mapRes)[0]['lat'], ' Hits: ', mapRes.hits, ' Results:', results.hits)
    return jsonify({ 'results': list(mapRes) })

def login():
    # Process the POST data
    data = request.json
    if data['username'] == 'admin' and data['password'] == 'admin123':
        return jsonify({'status': 'success', 'received_data': data})

    # Do something with the data
    return jsonify({'status': 'error', 'msg': 'username or password is incorrect.'})