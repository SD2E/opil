from .opil_factory import OPILFactory, Document, ValidationReport
from .uml_factory import UMLFactory
from .generate_opil_from_strateos import StrateosOpilGenerator
from .shacl_validator import ShaclValidator
import os
import posixpath

# Import ontology
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
default_ontology = posixpath.join(MODULE_PATH, 'rdf/opil.ttl')
opil_path = posixpath.join(os.path.dirname(os.path.realpath(__file__)), 'rdf/opil.ttl')
opil_factory = OPILFactory(locals(), opil_path, 'http://bioprotocols.org/opil/v1#')
