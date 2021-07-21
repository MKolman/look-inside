import flask

import queries
import config
import commands
from models import db

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
        if not chrom.isdigit():
            return flask.jsonify({
                'success': False,
                'message': 'Invalid search query. It should start with either "r" or a number.',
                'result': [],
            })
        genes_query = queries.genes_by_chrom_pos(int(chrom), pos[0] if pos else '')
    genes = []
    for gene in genes_query.limit(5):
        genes.append({
            'chromosome': gene.chromosome,
            'position': gene.position,
            'rsid': gene.id.strip(),
            'ref': gene.ref,
            'alt': gene.alt,
            'format': gene.format,
        })

    # Add user data if requested
    if (user_id := flask.request.args.get('user')).isdigit():
        all_rsids = [g['rsid'] for g in genes]
        genotypes = queries.get_genotype(int(user_id), all_rsids)
        mapping = {g.gene_location: g.value for g in genotypes}
        for gene in genes:
            gene['value'] = mapping.get(gene['rsid'], 'N/A')

    data = {
        'success': True,
        'result': genes,
    }
    return flask.jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
