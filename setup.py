from setuptools import setup
setup(name='dminer',
    version='0.0.1',
    description='Package to help mine and analyze information from darknet resources.',
    packages=[
        'dminer',
        'dminer.ingestion',
        'dminer.sinks',
        'dminer.sinks.helpers',
        'dminer.stores',
        'dminer.stores.configuration',
        'dminer.lib',
        'dminer.lib.deathbycaptcha'],
    scripts=['scripts/dminer']
)
