
from flask import render_template, current_app
import pysolr
import requests

from . import index

fields = index.solr_fields
TOKEN = 'pk.eyJ1IjoiaW1yYW5hc2lmIiwiYSI6ImNseDBjaTNtbTA1dDcyaXNjdjJsa2tlbWIifQ.2_kCycbjY-7_LrlucTewZw'

activity_fields = { 
                    "authority": "AUTHORITY", 
                    "activity": "ACTIVITY", 
                    "purpose": "PURPOSE/FOCUS", 
                    "context": "CONTEXT/FIELD OF ACTION",
                    "lines": "LINES",
                    "material": "MATERIAL",
                    "nature": "NATURE",
                    "denomination": "DENOMINATION",
                    "notes": "NOTES"
                }

def show(id):
    corename = current_app.config["SOLR_CORE"]

    solr = pysolr.Solr(corename)
    results = solr.search('id:'+id)
    data = results.docs[0]

    orig_dict = {}

    # Convert each value to string
    for key, value in data.items():
        if key == 'inscription': continue
        if key in activity_fields.keys(): continue

        orig_dict[key] = str(value)

        if not 'place_of_conception' in data.keys():
            orig_dict['place_of_conception'] = str(data['place_of_publication'])
        if not 'place_of_transaction' in data.keys():
            orig_dict['place_of_transaction'] = str(data['place_of_publication'])

    query = f'inscription:"{data["inscription"]}"'
    activities = solr.search(query, **{
        'rows': 0
    })

    activities = solr.search(query, **{
        'rows': activities.hits
    })

    print(activities.docs)

    if not any(any(key in d for key in activity_fields.keys()) for d in activities.docs):
        activities = []

    return render_template('show.html', item=orig_dict, activities=list(activities), activity_fields=activity_fields, fields=fields, mapbox_token = TOKEN)

def getOtherDatasourceRelations(tm_id):
    # Define the URL
    url = "https://www.trismegistos.org/dataservices/texrelations/uri/"+tm_id

    # Make a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()
        
        # Filter out fields that have non-null values
        filtered_data = {key: value for item in data for key, value in item.items() if value is not None}
        
        # Print the filtered data
        return filtered_data
    else:
        print(f"Failed to fetch data. HTTP Status code: {response.status_code}")
