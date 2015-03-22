# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from elasticsearch import Elasticsearch
from performance_tools.urls_flow.backends.base import BaseURLFlowBackend
from performance_tools.urls_flow.urls import normalize_url


class ElasticURLFlowBackend(BaseURLFlowBackend):
    def __init__(self, host='localhost', port=9200, username=None, password=None, protocol='http', query='*', date_from="", date_to=""):
        if username is not None and password is not None:
            self.url = '{}://{}:{}@{}:{:d}'.format(protocol, username, password, host, port)
        else:
            self.url = '{}://{}:{:d}'.format(protocol, host, port)

        self._backend = Elasticsearch([self.url])

        # Search body
        self._body = {
            "query": {
                "filtered": {
                    "query": {
                        "match_all": {}
                    },
                    "filter": {
                        "and": [
                            {
                                "query": {
                                    "query_string": {
                                        "query": query
                                    }
                                }
                            },
                            {
                                "range": {
                                    "@timestamp": {
                                        "gte": date_from,
                                        "lte": date_to,
                                    }
                                }
                            },
                        ]
                    }
                }
            }
        }

        # Search result batch size
        self._size = 50

        # Returned fields
        self._fields = [
            "referrer",
            "request"

        ]

        # Scrollable search
        self._search_type = 'scan'
        self._scroll = '1m'
        self._scroll_id = None

        super(ElasticURLFlowBackend, self).__init__()

    def extract_url_from_result(self, result):
        return [
            (normalize_url(hit['fields']['referrer'][0].strip('"')) or "-",
             normalize_url(hit['fields']['request'][0]) or "-")
            for hit in [i for i in result['hits']['hits'] if 'fields' in i]
        ]

    def __iter__(self):
        # Make first query
        result = self._backend.search(
            index='',
            doc_type='',
            body=self._body,
            size=self._size,
            fields=self._fields,
            search_type=self._search_type,
            scroll=self._scroll,
        )

        # Get total hits
        self._total_hits = result['hits']['total']

        # Get next scroll id
        self._scroll_id = result['_scroll_id']

        # Consume API first result
        yield result

        # Get next result
        result = self._backend.scroll(scroll=self._scroll, scroll_id=self._scroll_id)
        while result['hits']['hits']:
            # Get next scroll id
            self._scroll_id = result['_scroll_id']

            # Consume API next result
            yield result

            # Get next result
            result = self._backend.scroll(scroll=self._scroll, scroll_id=self._scroll_id)
