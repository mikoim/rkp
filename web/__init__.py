from flask import Flask, request, jsonify
from flask.ext.elasticsearch import FlaskElasticsearch

app = Flask(__name__)
es = FlaskElasticsearch(app)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', default='', type=str)
    limit = request.args.get('limit', default=100, type=int)
    reverse = request.args.get('reverse', default=False, type=bool)
    
    if limit > 100:
        limit = 100

    query = {
        'size': limit,
        'query': {
            'function_score': {
                'query': {
                    'simple_query_string': {
                        'query': keyword,
                        'fields': ['_all'],
                        'default_operator': 'and'
                    }
                },
                'functions': [
                    {
                        'script_score': {
                            'script': {
                                'lang': 'groovy',
                                'file': 'rkp-index',
                                'params': {
                                    'weight_a': 3,
                                    'weight_b': 2,
                                    'weight_c': 1,
                                    'weight_d': -1,
                                    'weight_f': -3
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

    if reverse:
        query['sort'] = [
            {
                '_score': {
                    'reverse': True
                }
            }
        ]

    result = es.search(index='rkp', body=query, filter_path='hits.hits._source')

    if 'hits' not in result:
        return jsonify(subjects=[]), 404

    subjects = [s['_source'] for s in result['hits']['hits']]

    return jsonify(subjects=subjects)
