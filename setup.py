from setuptools import setup

setup(name='PyOpil',
      description='Python package for demonstrating OPIL',
      version='0.0.1',
      install_requires=[
            'rdflib>=4.2.2'
            'rdflib-jsonld>=0.5.0'
            'sparqlwrapper>=1.8.5'
      ]
)