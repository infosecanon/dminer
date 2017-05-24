"""
The ingestion module provides support for all tasks relating to the parsing and
cleaning of data to be eventually imported into a particular datastore.
"""
import alphabay
import dreammarket

def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding subgroups for ingestion points.
    Subgroups provide the entry point for this parser.
    """
    ingestion_parsers = parser.add_subparsers()
    
    alphabay_ingestion_parser = ingestion_parsers.add_parser("alphabay", help=alphabay.__doc__)
    alphabay.prepare_cli(alphabay_ingestion_parser)
    
    dreammarket_ingestion_parser = ingestion_parsers.add_parser("dreammarket", help=dreammarket.__doc__)
    dreammarket.prepare_cli(dreammarket_ingestion_parser)
