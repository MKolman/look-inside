import flask
import config
import commands

from models import db

def make_app():
    app = flask.Flask(__name__)
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
    search_query = flask.request.args.get('q')
    if len(search_query) == 0:
        # Terminate search in case of empty search query
        return flask.jsonify({
            'success': False,
            'message': 'No search query provided.',
            'result': [],
        })

    data = {
        'success': True,
        'result': [{
            'chromosome': 1,
            'position': 2,
            'rsid': 'rs123',
            'ref': 'A',
            'alt': 'A',
            'format': 'q=' + search_query,
        }],
    }
    return flask.jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
