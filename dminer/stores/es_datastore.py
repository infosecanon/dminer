from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionTimeout

class ESDataStore(object):
    def __init__(self, host='localhost', port=9200):
        self.host = host
        self.port = port
        self.es = Elasticsearch([":".join([str(host), str(port)])])

    def create(self, *args, **kwargs):
        date_field = kwargs.get("index_date_field", None)
        parser = kwargs.get('parser', 'default')
        doctype = kwargs.get('type', 'default')
        document = kwargs.get('document', {})

        if date_field:
            index_date = document[date_field]
            # Index document into an index based on index_date field
            options = {
                "index": "dminer-%s-%s" % (parser, index_date),
                "doc_type": doctype,
                "body": document
            }
        else:
            options = {
                "index": "dminer-%s" % parser,
                "doc_type": doctype,
                "body": document
            }

        while True:
            try:
                value = self.es.index(**options)
            except ConnectionTimeout:
                print "Connection Timeout"
                continue
            break
        return value

    def find(self, *args, **kwargs):
        return self.es.search(*args, **kwargs)

    def delete(self, index, doctype, doc_id):
        raise NotImplementedError("Implement me, yo.")

    def update(self, index, doctype, doc_id, document):
        raise NotImplementedError("Implement me, yo.")
