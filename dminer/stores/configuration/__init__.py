"""
TODO: DOC
"""
import alphabay
import dreammarket
import master

def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding subgroups for datastore 
    configuration by each of the supported ingestion modules.
    """
    configuration_subparser = parser.add_subparsers()
    
    master_subparser = configuration_subparser.add_parser("master", help=master.__doc__)
    master.prepare_cli(master_subparser)
    
    alphabay_subparser = configuration_subparser.add_parser("alphabay", help=alphabay.__doc__)
    alphabay.prepare_cli(alphabay_subparser)
    
    dreammarket_subparser = configuration_subparser.add_parser("dreammarket", help=dreammarket.__doc__)
    dreammarket.prepare_cli(dreammarket_subparser)
