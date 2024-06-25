
from flask import render_template, current_app
import pysolr

from . import index

fields = index.solr_fields
TOKEN = 'pk.eyJ1IjoiaW1yYW5hc2lmIiwiYSI6ImNseDBjaTNtbTA1dDcyaXNjdjJsa2tlbWIifQ.2_kCycbjY-7_LrlucTewZw'

def show(id):
    corename = current_app.config["SOLR_CORE"]

    solr = pysolr.Solr(corename)
    results = solr.search('id:'+id)
    data = results.docs[0]

    # Convert each value to string
    for key, value in data.items():
            data[key] = str(value)

    return render_template('show.html', item=data, fields=fields, mapbox_token = TOKEN)
