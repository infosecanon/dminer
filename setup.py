from setuptools import setup
setup(name='dminer',
    version='0.0.1',
    description='Package to help mine and analyze information from darknet resources.',
    packages=[
        'dminer',
        # Ingestion related packages
        'dminer.ingestion',
        'dminer.ingestion.alphabay',
        'dminer.ingestion.dreammarket',
        'dminer.ingestion.helpers',
        # Sink related packages
        'dminer.sinks',
        'dminer.sinks.alphabay',
        'dminer.sinks.dreammarket',
        'dminer.sinks.helpers',
        # Store related Packages
        'dminer.stores',
        'dminer.stores.configuration',
        'dminer.stores.configuration.alphabay',
        'dminer.stores.configuration.dreammarket',
        'dminer.stores.configuration.master',
        'dminer.stores.interfaces',
        # 3rd party libraries
        'dminer.lib',
        'dminer.lib.deathbycaptcha'],
    scripts=['scripts/dminer']
)
