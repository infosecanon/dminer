"""
The stores module provides the ability to load and manage data into particular
data stores. It also provides configuration abilities to help facilitate the
interactions with the datastore.
"""
import configuration
import interfaces

def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding subgroups for configuration and
    interactions with various datastores.
    """
    stores_subparser = parser.add_subparsers()
    
    configuration_parser = stores_subparser.add_parser("config", help=configuration.__doc__)
    configuration.prepare_cli(configuration_parser)
