import os

from flask import Flask, render_template
import click


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SOLR_CORE='http://solr:8983/solr/inscriptions/'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Flask is working!'

    @app.route('/')
    @app.route('/about')
    def about():
        return render_template('about.html')

    from . import search
    app.add_url_rule('/results', 'results', search.results)
    #app.add_url_rule('/filters', 'filters', search.getAllFilters)
    app.add_url_rule('/map_results', 'map_results', search.getAllLatLang)

    from. import download
    app.add_url_rule('/query.csv', 'query_csv', download.downloadCSV)
    app.add_url_rule('/query.xlsx', 'query_xlsx', download.downloadExcel)
    app.add_url_rule('/query.xml', 'query_xml', download.downloadXML)
    app.add_url_rule('/query.json', 'query_json', download.downloadJSON)

    from . import item
    app.add_url_rule('/item/<id>', 'item', item.show)
    app.add_url_rule('/relation/<tm_id>', 'relation', item.getOtherDatasourceRelations)

    from . import editRecords
    app.add_url_rule('/edit_record/<id>', 'update_record', editRecords.update_record, methods=['POST'])
    app.add_url_rule('/edit_record/<id>', 'edit_record', editRecords.edit_record)
    app.add_url_rule('/login', 'login', editRecords.login, methods=['POST'])

    # CLI command
    from . import index
    @app.cli.command('index-csv')
    @click.argument('file')
    @click.option('--section', '-s', default='1')
    def index_csv(file, section):
        """Convert a CSV file to solr XML on STDOUT"""
        #print("File to index: "+file)
        index.index_csv(file, section)

    return app

