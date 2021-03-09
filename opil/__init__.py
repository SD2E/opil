from sbol_factory import SBOLFactory, Document, ValidationReport
from .generate_opil_from_strateos import StrateosOpilGenerator
import sbol3 as sbol
import os
import posixpath

# Import ontology
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
default_ontology = posixpath.join(MODULE_PATH, 'rdf/opil.ttl')
opil_path = posixpath.join(os.path.dirname(os.path.realpath(__file__)), 'rdf/opil.ttl')
SBOLFactory(locals(), opil_path, 'http://bioprotocols.org/opil/v1#')

