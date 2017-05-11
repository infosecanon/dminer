"""
The alphabay configuration module provides the ability to interact with datastores
containing - or eventually to contain - ingested alphabay data. This includes
viewing info about existing schemas & data, creating the schema in a blank
datastore, as well as deletion of existing data in a datastore.
"""
import elasticsearch

def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding subgroups for the various
    datastore backends supported by this configuration module.
    """
    alphabay_subparser = parser.add_subparsers()
    
    alphabay_elasticsearch_config_parser = alphabay_subparser.add_parser("elasticsearch", help=elasticsearch.__doc__)
    elasticsearch.prepare_cli(alphabay_elasticsearch_config_parser)
