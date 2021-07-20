import flask

import queries
import config
import commands
from models import db, GeneLocation

def make_app():
    app = flask.Flask(__name__)
    app.register_blueprint(commands.genome_bp)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.app_context().push()
    db.init_app(app)
    db.create_all()
    return app

app = make_app()

@app.get('/')
def index():
    """ Serve static HTML landing page """
    return flask.render_template('index.html')

@app.get('/api/search')
def search():
    """ Given a search query return up to 10 results that
    match either RSID or chromosome + position
    """
    search_query = flask.request.args.get('q').strip()
    if len(search_query) == 0:
        # Terminate search in case of empty search query
        return flask.jsonify({
            'success': False,
            'message': 'No search query provided.',
            'result': [],
        })
    
    if search_query.startswith('r'):
        genes_query = queries.genes_by_rsid_prefix(search_query)
    else:
        chrom, *pos = search_query.split(' ', 1)
        genes_query = queries.genes_by_chrom_pos(int(chrom), pos[0] if pos else '')
    genes_query = genes_query.limit(5)
    print(genes_query.statement.compile(compile_kwargs={"literal_binds": True}))
    genes = []
    for gene in genes_query:
        genes.append({
            'chromosome': gene.chromosome,
            'position': gene.position,
            'rsid': gene.id,
            'ref': gene.ref,
            'alt': gene.alt,
            'format': gene.format,
        })
    data = {
        'success': True,
        'result': genes,
    }
    return flask.jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
