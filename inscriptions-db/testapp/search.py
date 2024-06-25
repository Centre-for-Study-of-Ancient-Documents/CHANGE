
from flask import render_template, current_app
import pysolr


def results():
    corename = current_app.config["SOLR_CORE"]

    solr = pysolr.Solr(corename)
    #results = solr.search('city:Sardis')
    results = solr.search('*',rows=3000)
    return render_template('results.html', res=list(results))
