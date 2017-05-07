"""
"""
import elasticsearch

def prepare_cli(parser):
    """
    """
    alphabay_subparser = parser.add_subparsers()
    
    alphabay_elasticsearch_config_parser = alphabay_subparser.add_parser("elasticsearch", help=elasticsearch.__doc__)
    elasticsearch.prepare_cli(alphabay_elasticsearch_config_parser)
