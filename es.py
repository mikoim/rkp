from elasticsearch import Elasticsearch
from db import *


def main():
    es = Elasticsearch()
    db = DB()

    session = db.session()

    for x in session.query(Subject).yield_per(5):
        res = es.index(index='rkp', doc_type='subject', body=x.dict())

        if not res['created']:
            raise Exception


if __name__ == '__main__':
    main()
