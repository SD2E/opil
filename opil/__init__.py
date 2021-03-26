from sbol_factory import SBOLFactory, Document, ValidationReport, UMLFactory
from .generate_opil_from_strateos import StrateosOpilGenerator
import sbol3 as sbol
import os
import posixpath

# Import ontology
__factory__ = SBOLFactory(locals(), 
                          posixpath.join(os.path.dirname(os.path.realpath(__file__)),
                                         'rdf/opil.ttl'),
                          'http://bioprotocols.org/opil/v1#')
__umlfactory__ = UMLFactory(__factory__)
