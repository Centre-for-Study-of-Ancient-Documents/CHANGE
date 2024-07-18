
from flask import render_template, current_app, request, jsonify
import pysolr

# ====================================================================================================
solr_fields = [
        "region",
        "city",
        "place_of_publication",
        "place_of_conception",
        "place_of_transaction",
        "lat",
        "long",
        "reference",
        "reference_num",
        "reference_2",
        "reference_num_2",
        "reference_3",
        "reference_num_3",
        "bib_url",
        "date_from",
        "date_to",
        "description",
        "phi_url",
        "phi_url_2",
        "phi_id",
        "tm_id",
        "doc_type",
        "authority",
        "activity",
        "purpose",
        "context",
        "lines",
        "material",
        "nature",
        "denomination",
        "notes"
    ]

def edit_record(id):
    corename = current_app.config["SOLR_CORE"]
    solr = pysolr.Solr(corename)

    # Fetch the record from Solr
    results = solr.search(f'id:{id}')
    record = results.docs[0]
    return render_template('edit_record.html', record=record, solr_fields = solr_fields)

def update_record(id):
    corename = current_app.config["SOLR_CORE"]
    solr = pysolr.Solr(corename, always_commit=True)

    # Update the record in Solr
    updated_data = request.form.to_dict()
    updated_data['epigraphic_reference'] = updated_data['reference'] + ' ' + updated_data['reference_num']
    updated_data['id'] = id
    solr.add([updated_data])

    # Fetch the record from Solr
    results = solr.search(f'id:{id}')
    record = results.docs[0]

    return render_template('edit_record.html', record=record, solr_fields = solr_fields, message = 'Record updated.')

def login():
    # Process the POST data
    data = request.json
    if data['username'] == 'admin' and data['password'] == 'admin123':
        return jsonify({'status': 'success', 'received_data': data})

    # Do something with the data
    return jsonify({'status': 'error', 'msg': 'username or password is incorrect.'})