"""
The hansa configuration module provides the ability to interact with
datastores containing - or eventually to containing - ingested hansa data.
This includes viewing info about existing schemas & data, creating the schema in
a blank datastore, and deletion of existing data from a datastore.
"""
from elasticsearch import *

def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding subgroups for the various
    datastore backends supported by this configuration module.
    """
    hansa_subparser = parser.add_subparsers()

    hansa_elasticsearch_config_parser = hansa_subparser.add_parser(
        "elasticsearch",
        help=elasticsearch.__doc__
    )
    elasticsearch.prepare_cli(hansa_elasticsearch_config_parser)
