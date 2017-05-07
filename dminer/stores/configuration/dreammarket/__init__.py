"""
"""
from elasticsearch import *

def prepare_cli(parser):
    """
    """
    dreammarket_subparser = parser.add_subparsers()
    
    dreammarket_elasticsearch_config_parser = dreammarket_subparser.add_parser("elasticsearch", help=elasticsearch.__doc__)
    elasticsearch.prepare_cli(dreammarket_elasticsearch_config_parser)
