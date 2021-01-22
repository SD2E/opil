from setuptools import setup

# This version includes a patch that squelches logging in
# the opil factory, which was conflicting with logging in
# other modules

setup(name='opil',
      description='Python package for demonstrating OPIL',
      version='1.0a6',
      install_requires=[
            'sbol3==1.0a5',
            'rdflib>=5.0.0',
            'rdflib-jsonld>=0.5.0',
            'sparqlwrapper>=1.8.5',
            'pyshacl>=0.13.3',
            'python-dateutil>=2.8.1',
            'requests'
      ],
      packages=['opil'],
      package_data={'opil': ['rdf/*', 'sparql/*']},
      include_package_data=True,
#      entry_points = {
#            'rdf.plugins.sparqleval': [
#            'custom_eval =  custom_eval:customEval',
#        ],
#      }
)
