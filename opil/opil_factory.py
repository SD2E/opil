import sbol3 as sbol
from sbol3 import set_namespace
from sbol3 import CombinatorialDerivation, Component, Measure, VariableFeature
# pySBOL extension classes are aliased because they are not present in SBOL-OWL
from sbol3 import CustomTopLevel as TopLevel
from sbol3 import CustomIdentified as Identified

from .shacl_validator import ShaclValidator

import rdflib
import os
import posixpath
#import logging
from math import inf

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


def help():
    #logging.getLogger().setLevel(logging.INFO)
    print(OPILFactory.__doc__)



class OPILFactory():

    __doc__ = ''  # Documentation string

    @staticmethod
    def generate(class_uri):
        if Query.OPIL not in class_uri:
            return ''
        superclass_uri = Query.query_superclass(class_uri)
        OPILFactory.generate(superclass_uri)

        CLASS_URI = class_uri
        CLASS_NAME = sbol.utils.parse_class_name(class_uri)
        SUPERCLASS_NAME = sbol.utils.parse_class_name(superclass_uri)

        if CLASS_NAME in globals().keys():
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
            property_uris = Query.query_object_properties(CLASS_URI)
            compositional_properties = Query.query_compositional_properties(CLASS_URI)
            associative_properties = [uri for uri in property_uris if uri not in
                                        compositional_properties]

            # Initialize associative properties
            for property_uri in associative_properties:
                property_name = Query.query_label(property_uri).replace(' ', '_')
                cardinality = Query.query_cardinality(property_uri, CLASS_URI)
                if len(cardinality):
                    upper_bound = 1
                else:
                    upper_bound = inf
                self.__dict__[property_name] = sbol.ReferencedObject(self, property_uri, 0, upper_bound)

            # Initialize compositional properties
            for property_uri in compositional_properties:
                property_name = Query.query_label(property_uri).replace(' ', '_')
                cardinality = Query.query_cardinality(property_uri, CLASS_URI)
                if len(cardinality):
                    upper_bound = 1
                else:
                    upper_bound = inf
                self.__dict__[property_name] = sbol.OwnedObject(self, property_uri, 0, upper_bound)

            # Initialize datatype properties
            property_uris = Query.query_datatype_properties(CLASS_URI)
            for property_uri in property_uris:
                property_name = Query.query_label(property_uri).replace(' ', '_')

                # Get the datatype of this property
                datatypes = Query.query_property_datatype(property_uri, CLASS_URI)
                if len(datatypes) == 0:
                    continue
                if len(datatypes) > 1:  # This might indicate an error in the ontology
                    raise

                # Get the cardinality of this datatype property
                cardinality = Query.query_cardinality(property_uri, CLASS_URI)
                if len(cardinality):
                    upper_bound = 1
                else:
                    upper_bound = inf

                if datatypes[0] == 'http://www.w3.org/2001/XMLSchema#string':
                    self.__dict__[property_name] = sbol.TextProperty(self, property_uri, 0, upper_bound)
                elif datatypes[0] == 'http://www.w3.org/2001/XMLSchema#int':
                    self.__dict__[property_name] = sbol.IntProperty(self, property_uri, 0, upper_bound)                    
                elif datatypes[0] == 'http://www.w3.org/2001/XMLSchema#boolean':
                    self.__dict__[property_name] = sbol.BooleanProperty(self, property_uri, 0, upper_bound)
                elif datatypes[0] == 'http://www.w3.org/2001/XMLSchema#anyURI':
                    self.__dict__[property_name] = sbol.URIProperty(self, property_uri, 0, upper_bound)

        # Instantiate metaclass
        attribute_dict = {}
        attribute_dict['__init__'] = __init__
        Class = type(CLASS_NAME, (globals()[SUPERCLASS_NAME],), attribute_dict)
        globals()[CLASS_NAME] = Class
        sbol.Document.register_builder(str(CLASS_URI), Class)

        # Print out properties -- this is for logging only
        property_uris = Query.query_object_properties(CLASS_URI)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            datatype = Query.query_property_datatype(property_uri, CLASS_URI)
            if len(datatype):
                datatype = sbol.utils.parse_class_name(datatype[0])
            else:
                datatype = None
            # cardinality = Query.query_cardinality(property_uri, rdf_type)
            # if len(cardinality):
            #     datatype = f'list of {datatype}'
            log += f'\t{property_name}\t{datatype}\n'
        property_uris = Query.query_datatype_properties(CLASS_URI)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            datatype = Query.query_property_datatype(property_uri, CLASS_URI)
            if len(datatype):
                datatype = sbol.utils.parse_class_name(datatype[0])
            else:
                datatype = None
            cardinality = Query.query_cardinality(property_uri, CLASS_URI)            

        return log

class Query():
    filename='sbol.rdf'
    OWL = rdflib.URIRef('http://www.w3.org/2002/07/owl#')
    RDF = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    SBOL = rdflib.URIRef('http://sbols.org/v2#')
    OPIL = rdflib.URIRef('http://bbn.com/synbio/opil#')
    graph = rdflib.Graph()
    graph.parse(posixpath.join(os.path.dirname(os.path.realpath(__file__)), 'rdf/opil.ttl'), format ='ttl')
    graph.parse(posixpath.join(os.path.dirname(os.path.realpath(__file__)), 'rdf/sbol3.ttl'), format ='ttl')
    graph.namespace_manager.bind('sbol', SBOL)
    graph.namespace_manager.bind('opil', OPIL)
    graph.namespace_manager.bind('tawny', rdflib.URIRef('http://www.purl.org/ontolink/tawny#'))
    graph.namespace_manager.bind('owl', rdflib.URIRef('http://www.w3.org/2002/07/owl#'))
    graph.namespace_manager.bind('rdfs', rdflib.URIRef('http://www.w3.org/2000/01/rdf-schema#'))
    graph.namespace_manager.bind('rdf', rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
    graph.namespace_manager.bind('xsd', rdflib.URIRef('http://www.w3.org/2001/XMLSchema#'))

    # for s in graph.subjects(RDF + rdflib.URIRef('type'), OWL + rdflib.URIRef('Class')):
    #     logging.info(s)

    prefixes = '''PREFIX sbol: <http://sbols.org/v2#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX tawny: <http://www.purl.org/ontolink/tawny#>
    PREFIX xml: <http://www.w3.org/XML/1998/namespace>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#">
    '''

    def query_base_class(cls):
        try:
            superclass = Query.query_superclass(cls)
            return Query.query_base_class(superclass)
        except Exception as e:
            return cls

    @staticmethod
    def query_base_classes():
        class_list = Query.query_classes()
        base_classes = set()
        for cls in class_list:
            base_class = Query.query_base_class(cls)
            base_classes.add(base_class)
        return list(base_classes)

    @staticmethod
    def query_classes():
        query = '''
            SELECT distinct ?cls 
            WHERE 
            {{
                ?cls rdf:type owl:Class . 
            }}
            '''.format(str(Query.OPIL))
        response = Query.graph.query(query)
        sbol_types = [str(row[0]) for row in response]
        return sbol_types

    @staticmethod
    def query_subclasses(superclass):
        query = '''
            SELECT distinct ?subclass 
            WHERE 
            {{
                ?subclass rdf:type owl:Class .
                ?subclass rdfs:subClassOf <{}>
            }}
            '''.format(superclass)
        response = Query.graph.query(query)
        subclasses = [row[0] for row in response]
        return subclasses

    @staticmethod
    def query_superclass(subclass):
        query = '''
            SELECT distinct ?superclass 
            WHERE 
            {{
                ?superclass rdf:type owl:Class .
                <{}> rdfs:subClassOf ?superclass
            }}
            '''.format(subclass)
        response = Query.graph.query(query)
        if len(response) == 0:
            raise Exception('{} has no superclass'.format(subclass))
        if len(response) > 1:
            raise Exception('{} has more than one superclass'.format(subclass))
        for row in response:
            superclass = str(row[0])
        return superclass

    @staticmethod
    def query_object_properties(class_uri):
        query =     '''
            SELECT distinct ?property_uri
            WHERE 
            {{
                ?property_uri rdf:type owl:ObjectProperty .
                ?property_uri rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* <{}>.
            }}
            '''.format(class_uri)
        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        property_types = response

        # The type of inherited properties are sometimes overridden 
        query = '''
            SELECT distinct ?property_uri
            WHERE 
            {{
                ?property_uri rdf:type owl:ObjectProperty .
                <{}> rdfs:subClassOf ?restriction .
                ?restriction owl:onProperty ?property_uri .
            }}
            '''.format(class_uri) 
        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        property_types.extend(response)
        return list(set(property_types))

    @staticmethod
    def query_compositional_properties(class_uri):
        query = '''
            SELECT distinct ?property_uri
            WHERE 
            {{
                ?property_uri rdf:type owl:ObjectProperty .
                ?property_uri rdfs:subPropertyOf opil:compositionalProperty .
                ?property_uri rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* <{}>.
            }}
            '''.format(class_uri)

        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        property_types = response

        # The type of inherited properties are sometimes overridden 
        query = '''
            SELECT distinct ?property_uri
            WHERE 
            {{
                ?property_uri rdf:type owl:ObjectProperty .
                ?property_uri rdfs:subPropertyOf opil:compositionalProperty .
                <{}> rdfs:subClassOf ?restriction .
                ?restriction owl:onProperty ?property_uri .
            }}
            '''.format(class_uri)
        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        property_types.extend(response) 
        return property_types

    @staticmethod
    def query_datatype_properties(class_uri):
        query =     '''
            SELECT distinct ?property_uri
            WHERE 
            {{
                ?property_uri rdf:type owl:DatatypeProperty .
                ?property_uri rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* <{}>.
            }}
            '''.format(class_uri)
        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        property_types = response

        # The type of inherited properties are sometimes overridden 
        query = '''
            SELECT distinct ?property_uri
            WHERE 
            {{
                ?property_uri rdf:type owl:DatatypeProperty .
                <{}> rdfs:subClassOf ?restriction .
                ?restriction owl:onProperty ?property_uri .
            }}
            '''.format(class_uri) 
        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        property_types.extend(response)
        return list(set(property_types))

    @staticmethod
    def query_cardinality(property_uri, class_uri):
        query = '''
            SELECT distinct ?cardinality
            WHERE 
            {{
                <{}> rdfs:subClassOf ?restriction .
                ?restriction rdf:type owl:Restriction .
                ?restriction owl:onProperty <{}> .
                ?restriction owl:maxCardinality ?cardinality .
            }}
            '''.format(class_uri, property_uri)
        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        cardinality = response
        return cardinality

    @staticmethod
    def query_property_datatype(property_uri, class_uri):
        query = '''
            SELECT distinct ?datatype
            WHERE 
            {{
                <{}> rdfs:subClassOf ?restriction .
                ?restriction rdf:type owl:Restriction .
                ?restriction owl:allValuesFrom ?datatype .
                ?restriction owl:onProperty <{}> .
            }}
            '''.format(class_uri, property_uri)    
        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        datatypes = response

        query = '''
            SELECT distinct ?datatype
            WHERE 
            {{
                <{}> rdfs:domain <{}> .
                <{}> rdfs:range ?datatype 
            }}
            '''.format(property_uri, class_uri, property_uri)    
        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        datatypes.extend(response)
        datatypes = list(set(datatypes))
        #if len(datatypes) == 0:
        #    logging.warn(f'{property_uri} datatype is undefined')
        #if len(datatypes) > 1:
        #    logging.warn(f'{property_uri} has more than one datatype')
        return list(set(datatypes))

    @staticmethod
    def query_label(property_uri):
        query =     '''
            SELECT distinct ?property_name
            WHERE 
            {{
                <{}> rdfs:label ?property_name
            }}
            '''.format(property_uri)    
        response = Query.graph.query(query)
        response = [str(row[0]) for row in response]
        if len(response) == 0:
            raise Exception(f'{property_uri} has no label')
        if len(response) > 1:
            raise Exception(f'{property_uri} has more than one label')
        property_name = response[0]
        return property_name


log = ''
for class_uri in Query.query_classes():
    log += OPILFactory.generate(class_uri)
OPILFactory.__doc__ = log
