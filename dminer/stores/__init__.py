"""
TODO: DOC
"""
import configuration
import interfaces

def prepare_cli(parser):
    """
    TODO: DOC
    """
    stores_subparser = parser.add_subparsers()
    
    configuration_parser = stores_subparser.add_parser("config", help=configuration.__doc__)
    configuration.prepare_cli(configuration_parser)
