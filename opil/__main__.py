import os
import posixpath

# Import ontology
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
default_ontology = posixpath.join(MODULE_PATH, 'rdf/opil.ttl')
opil_path = posixpath.join(os.path.dirname(os.path.realpath(__file__)), 'rdf/opil.ttl')
UMLFactory(__factory__, 'http://bioprotocols.org/opil/v1#')
