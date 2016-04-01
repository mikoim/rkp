from flask import Flask, request, jsonify
from flask.ext.elasticsearch import FlaskElasticsearch

app = Flask(__name__)
es = FlaskElasticsearch(app)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    query = {
        "size": 50,
        "query": {
            "function_score": {
                "query": {
                    "simple_query_string": {
                        "query": keyword,
                        "fields": ["_all"],
                        "default_operator": "and"
                    }
                },
                "functions": [
                    {
                        "script_score": {
                            "script": {
                                "lang": "groovy",
                                "file": "rkp-index",
                                "params": {
                                    "weight_a": 2,
                                    "weight_b": 1,
                                    "weight_c": 0,
                                    "weight_d": -4,
                                    "weight_f": -3
                                }
                            }
                        }
                    }
                ]
            }
        }
    }
    result = es.search(index='rkp', body=query, filter_path='hits.hits._source')

    if 'hits' not in result:
        return jsonify(subjects=[])

    subjects = [s['_source'] for s in result['hits']['hits']]

    return jsonify(subjects=subjects)