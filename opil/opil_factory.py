import sbol3 as sbol
from sbol3 import set_namespace
from sbol3 import CombinatorialDerivation, Component, Measure, VariableFeature
# pySBOL extension classes are aliased because they are not present in SBOL-OWL
from sbol3 import CustomTopLevel as TopLevel
from sbol3 import CustomIdentified as Identified

from .query import Query
from .shacl_validator import ShaclValidator

import rdflib
import posixpath
import os
#import logging

# Expose Document through the OPIL API
class Document(sbol.Document):

    def __init__(self):
        super(Document, self).__init__()
        self._validator = ShaclValidator()        

    def validate(self):
        conforms, results_graph, results_txt = self._validator.validate(self.graph())
        return ValidationReport(conforms, results_txt)


class ValidationReport():

    def __init__(self, is_valid, results_txt):
        self.is_valid = is_valid
        self.results = results_txt
        self.message = ''
        if not is_valid:
            i_message = results_txt.find('Message: ') + 9
            self.message = results_txt[i_message:]

    def __repr__(self):
        return self.message

#logging.basicConfig(level=logging.CRITICAL)


# def help():
#     #logging.getLogger().setLevel(logging.INFO)
#     print(OPILFactory.__doc__)



class OPILFactory():

    def __init__(self, ontology_path, ontology_namespace, verbose=False):
        self.namespace = rdflib.URIRef(ontology_namespace)
        self.query = Query(ontology_path)
        self.doc = ''
        docstring = ''
        for class_uri in self.query.query_classes():
            docstring += self.generate(class_uri)
        if verbose:
            print(docstring)

    def generate(self, class_uri):

        if self.namespace not in class_uri: 
            return ''
        superclass_uri = self.query.query_superclass(class_uri)
        self.generate(superclass_uri)  # Recurse into superclasses

        CLASS_URI = class_uri
        CLASS_NAME = sbol.utils.parse_class_name(class_uri)
        SUPERCLASS_NAME = sbol.utils.parse_class_name(superclass_uri)

        if CLASS_NAME in globals().keys():  # Abort if the class has already been generated
            return ''

        #Logging
        log = f'\n{CLASS_NAME}\n'
        log += '-' * (len(log) - 2) + '\n'

        # Define constructor
        def __init__(self, identity=None, type_uri=CLASS_URI):
            Base = globals()[SUPERCLASS_NAME]
            Base.__init__(self, identity=identity, type_uri=CLASS_URI)
            self.type_uri = CLASS_URI

            # Object properties can be either compositional or associative
            property_uris = self.query.query_object_properties(CLASS_URI)
            compositional_properties = self.query.query_compositional_properties(CLASS_URI)
            associative_properties = [uri for uri in property_uris if uri not in
                                        compositional_properties]

            # Initialize associative properties
            for property_uri in associative_properties:
                property_name = self.query.query_label(property_uri).replace(' ', '_')
                lower_bound, upper_bound = self.query.query_cardinality(property_uri, CLASS_URI)
                self.__dict__[property_name] = sbol.ReferencedObject(self, property_uri, lower_bound, upper_bound)

            # Initialize compositional properties
            for property_uri in compositional_properties:
                property_name = self.query.query_label(property_uri).replace(' ', '_')
                lower_bound, upper_bound = self.query.query_cardinality(property_uri, CLASS_URI)
                self.__dict__[property_name] = sbol.OwnedObject(self, property_uri, lower_bound, upper_bound)

            # Initialize datatype properties
            property_uris = self.query.query_datatype_properties(CLASS_URI)
            for property_uri in property_uris:
                property_name = self.query.query_label(property_uri).replace(' ', '_')

                # Get the datatype of this property
                datatypes = self.query.query_property_datatype(property_uri, CLASS_URI)
                if len(datatypes) == 0:
                    continue
                if len(datatypes) > 1:  # This might indicate an error in the ontology
                    raise

                # Get the cardinality of this datatype property
                lower_bound, upper_bound = self.query.query_cardinality(property_uri, CLASS_URI)
                if datatypes[0] == 'http://www.w3.org/2001/XMLSchema#string':
                    self.__dict__[property_name] = sbol.TextProperty(self, property_uri, lower_bound, upper_bound)
                elif datatypes[0] == 'http://www.w3.org/2001/XMLSchema#int':
                    self.__dict__[property_name] = sbol.IntProperty(self, property_uri, lower_bound, upper_bound)                    
                elif datatypes[0] == 'http://www.w3.org/2001/XMLSchema#boolean':
                    self.__dict__[property_name] = sbol.BooleanProperty(self, property_uri, lower_bound, upper_bound)
                elif datatypes[0] == 'http://www.w3.org/2001/XMLSchema#anyURI':
                    self.__dict__[property_name] = sbol.URIProperty(self, property_uri, lower_bound, upper_bound)

        # Instantiate metaclass
        attribute_dict = {}
        attribute_dict['__init__'] = __init__
        Class = type(CLASS_NAME, (globals()[SUPERCLASS_NAME],), attribute_dict)
        globals()[CLASS_NAME] = Class
        sbol.Document.register_builder(str(CLASS_URI), Class)

        # Print out properties -- this is for logging only
        property_uris = self.query.query_object_properties(CLASS_URI)
        for property_uri in property_uris:
            property_name = self.query.query_label(property_uri).replace(' ', '_')
            datatype = self.query.query_property_datatype(property_uri, CLASS_URI)
            if len(datatype):
                datatype = sbol.utils.parse_class_name(datatype[0])
            else:
                datatype = None
            lower_bound, upper_bound = self.query.query_cardinality(property_uri, CLASS_URI)
            log += f'\t{property_name}\t{datatype}\t{lower_bound}\t{upper_bound}\n'
        property_uris = self.query.query_datatype_properties(CLASS_URI)
        for property_uri in property_uris:
            property_name = self.query.query_label(property_uri).replace(' ', '_')
            datatype = self.query.query_property_datatype(property_uri, CLASS_URI)
            if len(datatype):
                datatype = sbol.utils.parse_class_name(datatype[0])
            else:
                datatype = None
            lower_bound, upper_bound = self.query.query_cardinality(property_uri, CLASS_URI)            
            log += f'\t{property_name}\t{datatype}\t{lower_bound}\t{upper_bound}\n'

        return log

if __package__:
    opil_path = posixpath.join(os.path.dirname(os.path.realpath(__file__)), 'rdf/opil.ttl')
    o = OPILFactory(opil_path, Query.OPIL)
