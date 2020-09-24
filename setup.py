from setuptools import setup

setup(name='opil_demo',
      description='Python package for demonstrating OPIL',
      version='0.0.1',
      install_requires=[
            'rdflib>=4.2.2'
            'rdflib-jsonld>=0.5.0'
            'sparqlwrapper>=1.8.5'
            'pyshacl>=0.13.3'
            'python-dateutil>=2.8.1'
      ],
      packages=['opil', 'opil_demo'],
      package_data={'opil_demo': ['rdf/*', 'sparql/*']},
      include_package_data=True,
      entry_points = {
            'rdf.plugins.sparqleval': [
            'custom_eval =  custom_eval:customEval',
        ],
      }
)
