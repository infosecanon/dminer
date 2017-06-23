"""
The master store configuration module allows for interaction with datastores
to cascade across all supported configuration interfaces.
"""
import elasticsearch


def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding subgroups for the various
    datastore backends supported by this configuration module.
    """
    master_subparsers = parser.add_subparsers()
    
    master_elasticsearch_subparser = master_subparsers.add_parser("elasticsearch", help=elasticsearch.__doc__)
    elasticsearch.prepare_cli(master_elasticsearch_subparser)
