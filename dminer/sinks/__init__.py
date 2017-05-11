"""
The sinks (scrape) module provides the ability to collect data across various data sources.
This data can then be passed to an ingestion point for futher processing and
eventual storage.
"""
import alphabay
import dreammarket

def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding subgroups for the various sinks.
    Subgroups provide the entry point for this parser.
    """
    sink_parsers = parser.add_subparsers()
    
    alphabay_sink_parser = sink_parsers.add_parser("alphabay", help=alphabay.__doc__)
    alphabay.prepare_cli(alphabay_sink_parser)
    
    dreammarket_sink_parser = sink_parsers.add_parser("dreammarket", help=dreammarket.__doc__)
    dreammarket.prepare_cli(dreammarket_sink_parser)
