import sbol3 as sbol
from sbol3 import set_namespace

import rdflib
import os
import posixpath
#import logging
from .shacl_validator import ShaclValidator

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

#logging.basicConfig(level=logging.CRITICAL)


def help():
    #logging.getLogger().setLevel(logging.INFO)
    OPILFactory.generate()


class OPILFactory():

    @staticmethod
    def generate():
        opil_types = Query.query_base_classes()
        for opil_type in opil_types:
            OPILFactory.create_base_class(opil_type)
            OPILFactory.create_derived_classes(opil_type)

    def create_base_class(rdf_type):
        "Create subclass using the 'type' metaclass"
        def __init__(self, name=None, type_uri=rdf_type):
            if name is None:
                raise ValueError('Cannot instantiate {rdf_type} object. Please specify a URI')
            sbol.TopLevel.__init__(self, name=name, type_uri=rdf_type)
            self.__dict__['name'] = sbol.TextProperty(self, str(Query.OPIL + 'name'),
                                                      0, 1, [])

            # Object properties can be either compositional or associative
            property_uris = Query.query_object_properties(rdf_type)
            compositional_properties = Query.query_compositional_properties(rdf_type)
            associative_properties = [uri for uri in property_uris if uri not in
                                        compositional_properties]

            # Initialize associative properties
            for property_uri in associative_properties:
                property_name = Query.query_label(property_uri).replace(' ', '_')
                cardinality = Query.query_cardinality(property_uri, rdf_type)
                if len(cardinality):
                    upper_bound = 1
                else:
                    upper_bound = inf
                self.__dict__[property_name] = sbol.ReferencedObject(self, property_uri, 0, upper_bound)

            # Initialize compositional properties
            for property_uri in compositional_properties:
                property_name = Query.query_label(property_uri).replace(' ', '_')
                cardinality = Query.query_cardinality(property_uri, rdf_type)
                if len(cardinality):
                    upper_bound = 1
                else:
                    upper_bound = inf
                self.__dict__[property_name] = sbol.OwnedObject(self, property_uri, 0, upper_bound)

            # Initialize datatype properties
            property_uris = Query.query_datatype_properties(rdf_type)
            for property_uri in property_uris:
                property_name = Query.query_label(property_uri).replace(' ', '_')

                # Get the datatype of this property
                datatypes = Query.query_property_datatype(property_uri, rdf_type)
                if len(datatypes) == 0:
                    continue
                if len(datatypes) > 1:
                    continue

                # Get the cardinality of this datatype property
                cardinality = Query.query_cardinality(property_uri, rdf_type)
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

        class_name = sbol.utils.parse_class_name(rdf_type)
        log = f'\n{class_name}\n'
        log += '-' * (len(log) - 2) + '\n'

        # Query and instantiate properties
        attribute_dict = {}
        attribute_dict['__init__'] = __init__
        sbol_toplevel = type(class_name, (sbol.TopLevel, ), attribute_dict)
        globals()[class_name] = sbol_toplevel
        sbol.Document.register_builder(str(rdf_type), sbol_toplevel)

        # Print out properties -- this is for logging only
        property_uris = Query.query_object_properties(rdf_type)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            datatype = Query.query_property_datatype(property_uri, rdf_type)
            if len(datatype):
                datatype = sbol.utils.parse_class_name(datatype[0])
            else:
                datatype = None
            # cardinality = Query.query_cardinality(property_uri, rdf_type)
            # if len(cardinality):
            #     datatype = f'list of {datatype}'
            log += f'\t{property_name}\t{datatype}\n'

        property_uris = Query.query_datatype_properties(rdf_type)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            datatype = Query.query_property_datatype(property_uri, rdf_type)
            if len(datatype):
                datatype = sbol.utils.parse_class_name(datatype[0])
            else:
                datatype = None
            cardinality = Query.query_cardinality(property_uri, rdf_type)
            # if len(cardinality):
            #     datatype = f'list of {datatype}'
            # log += f'\t{property_name}\t{datatype}\n'

        #if logging.getLogger().level == logging.INFO:
        #    print(log.rstrip())

        return sbol_toplevel

    def create_derived_class(rdf_type):
        CLASS_NAME = sbol.utils.parse_class_name(rdf_type)
        SUPERCLASS_NAME = sbol.utils.parse_class_name(Query.query_superclass(rdf_type))

        def __init__(self, name=None, type_uri=rdf_type):
            if name is None:
                raise ValueError('Cannot instantiate {rdf_type} object. Please specify a URI')
            Base = globals()[SUPERCLASS_NAME]
            Base.__init__(self, name)
            self.type_uri = rdf_type

            # Object properties can be either compositional or associative
            property_uris = Query.query_object_properties(rdf_type)
            compositional_properties = Query.query_compositional_properties(rdf_type)
            associative_properties = [uri for uri in property_uris if uri not in
                                        compositional_properties]

            # Initialize associative properties
            for property_uri in associative_properties:
                property_name = Query.query_label(property_uri).replace(' ', '_')
                cardinality = Query.query_cardinality(property_uri, rdf_type)
                if len(cardinality):
                    upper_bound = 1
                else:
                    upper_bound = inf
                self.__dict__[property_name] = sbol.ReferencedObject(self, property_uri, 0, upper_bound)

            # Initialize compositional properties
            for property_uri in compositional_properties:
                property_name = Query.query_label(property_uri).replace(' ', '_')
                cardinality = Query.query_cardinality(property_uri, rdf_type)
                if len(cardinality):
                    upper_bound = 1
                else:
                    upper_bound = inf
                self.__dict__[property_name] = sbol.OwnedObject(self, property_uri, 0, upper_bound)

            # Initialize datatype properties
            property_uris = Query.query_datatype_properties(rdf_type)
            for property_uri in property_uris:
                property_name = Query.query_label(property_uri).replace(' ', '_')

                # Get the datatype of this property
                datatypes = Query.query_property_datatype(property_uri, rdf_type)
                if len(datatypes) == 0:
                    continue
                if len(datatypes) > 1:
                    continue

                # Get the cardinality of this datatype property
                cardinality = Query.query_cardinality(property_uri, rdf_type)
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

        # Query and instantiate properties
        attribute_dict = {}
        attribute_dict['__init__'] = __init__

        log = f'\n{CLASS_NAME}\n'
        log += '-' * (len(log) - 2) + '\n'
        Class = type(CLASS_NAME, (globals()[SUPERCLASS_NAME],), attribute_dict)
        globals()[CLASS_NAME] = Class
        sbol.Document.register_builder(str(rdf_type), Class)

        # Print out properties -- this is for logging only
        property_uris = Query.query_object_properties(rdf_type)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            datatype = Query.query_property_datatype(property_uri, rdf_type)
            if len(datatype):
                datatype = sbol.utils.parse_class_name(datatype[0])
            else:
                datatype = None
            # cardinality = Query.query_cardinality(property_uri, rdf_type)
            # if len(cardinality):
            #     datatype = f'list of {datatype}'
            log += f'\t{property_name}\t{datatype}\n'
        property_uris = Query.query_datatype_properties(rdf_type)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            datatype = Query.query_property_datatype(property_uri, rdf_type)
            if len(datatype):
                datatype = sbol.utils.parse_class_name(datatype[0])
            else:
                datatype = None
            cardinality = Query.query_cardinality(property_uri, rdf_type)
            # if len(cardinality):
            #     datatype = f'list of {datatype}'
            # log += f'\t{property_name}\t{datatype}\n'

        #if logging.getLogger().level == logging.INFO:
        #    print(log.rstrip())

    def create_derived_classes(base_class):
        rdf_subtypes = Query.query_subclasses(base_class)
        for rdf_subtype in rdf_subtypes:
            OPILFactory.create_derived_class(rdf_subtype)
            OPILFactory.create_derived_classes(rdf_subtype)


class Query():
    filename='sbol.rdf'
    OWL = rdflib.URIRef('http://www.w3.org/2002/07/owl#')
    RDF = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    SBOL = rdflib.URIRef('http://sbols.org/v2#')
    OPIL = rdflib.URIRef('http://bbn.com/synbio/opil#')
    graph = rdflib.Graph()
    graph.parse(posixpath.join(os.path.dirname(os.path.realpath(__file__)), 'rdf/opil.ttl'), format ='ttl')
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

OPILFactory.generate()
