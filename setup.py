from setuptools import setup

setup(name='MyRdflib',
      description='RDF package for CREATE',
      packages=['rdf_create'],
      version='0.0.1',
      install_requires=[
            'rdflib>=5.0.0'
            'rdflib-jsonld>=0.5.0'
            'sparqlwrapper>=1.8.5'
      ]
)