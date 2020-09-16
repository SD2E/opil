import pySBOL3.sbol3 as sbol
import rdflib

def parse_class_name(uri):
    if '#' in uri:
        return uri[uri.rindex('#')+1:]
    elif '/' in uri:
        return uri[uri.rindex('/')+1:]
    else:
        return ''

# class SBOLObject():
#     def __init__(self, *args):
#         print('Instantiating SBOLObject')

# class Identified(SBOLObject):
#     def __init__(self, *args):
#         SBOLObject.__init__(*args)
#         print('Instantiating Identified')

class OPILFactory():

    def create_base_class(rdf_type):
        "Create subclass using the 'type' metaclass"
        def __init__(self, uri):
            sbol.SBOLObject.__init__(self, uri, rdf_type)

        class_name = parse_class_name(rdf_type)
        print('Defining %s class' %class_name)

        # Query and instantiate properties
        attribute_dict = {}
        attribute_dict['__init__'] = __init__
        property_uris = Query.query_object_properties(rdf_type)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            attribute_dict[property_name] = 'foo'
            print('\t{}'.format(property_name))
        property_uris = Query.query_datatype_properties(rdf_type)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            attribute_dict[property_name] = 'foo'
            print('\t{}'.format(property_name))

        sbol_toplevel = type(class_name, (), attribute_dict)
        globals()[class_name] = sbol_toplevel
        return sbol_toplevel

    def create_derived_class(rdf_type):
        CLASS_NAME = parse_class_name(rdf_type)
        SUPERCLASS_NAME = parse_class_name(Query.query_superclass(rdf_type))

        def __init__(self, uri):
            Base = globals()[SUPERCLASS_NAME]
            Base.__init__(self, uri)

        # Query and instantiate properties
        attribute_dict = {}
        attribute_dict['__init__'] = __init__
        property_uris = Query.query_object_properties(rdf_type)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            attribute_dict[property_name] = 'foo'
            print('\t{}'.format(property_name))
        property_uris = Query.query_datatype_properties(rdf_type)
        for property_uri in property_uris:
            property_name = Query.query_label(property_uri).replace(' ', '_')
            attribute_dict[property_name] = 'foo'
            print('\t{}'.format(property_name))

        print('Defining %s class' %CLASS_NAME)
        Class = type(CLASS_NAME, (globals()[SUPERCLASS_NAME],), attribute_dict)
        globals()[CLASS_NAME] = Class

    def create_derived_classes(base_class):
        # try:
        #     superclass = Query.query_superclass(rdf_type)
        # except Exception as e:
        #     return
        rdf_subtypes = Query.query_subclasses(base_class)
        for rdf_subtype in rdf_subtypes:
            OPILFactory.create_derived_class(rdf_subtype)
            OPILFactory.create_derived_classes(rdf_subtype)

# def create_identified(rdf_type):
#     "Create subclass using the 'type' metaclass"
#     def __init__(self, uri):
#         Identified.__init__(self, uri)
#     class_name = parseClassName(rdf_type)
#     sbol_identified = type(class_name, (), dict(__init__ = __init__))
#     globals()[class_name] = sbol_identified
#     return sbol_identified



# def create_derived_classes(rdf_type):
#     "Create subclass using the 'type' metaclass"
#     SUPERCLASS_NAME = parseClassName(rdf_type)

#     sub_rdf_types = Query.query_subclasses(rdf_type)
#     for sub_rdf_type in sub_rdf_types:
#         SUBCLASS_NAME = parseClassName(sub_rdf_type)

#         def __init__(self, uri):
#             Base = globals()[SUPERCLASS_NAME]
#             Base.__init__(self, uri)
#             print('Instantiating %s' %SUBCLASS_NAME)

#         print('Creating %s' %SUBCLASS_NAME)

#         Subclass = type(SUBCLASS_NAME, (globals()[SUPERCLASS_NAME],), dict(__init__ = __init__))
#         globals()[SUBCLASS_NAME] = Subclass
#         Subclass('foo')
#         create_derived_classes(sub_rdf_type)

class Query():
    filename='sbol.rdf'
    OWL = rdflib.URIRef('http://www.w3.org/2002/07/owl#')
    RDF = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    SBOL = rdflib.URIRef('http://sbols.org/v2#')
    OPIL = rdflib.URIRef('http://bbn.com/synbio/opil#')
    graph = rdflib.Graph()
    graph.parse('opil_demo/rdf/opil.ttl', format ='ttl')
    graph.namespace_manager.bind('sbol', SBOL)
    graph.namespace_manager.bind('opil', OPIL)
    graph.namespace_manager.bind('tawny', rdflib.URIRef('http://www.purl.org/ontolink/tawny#'))
    graph.namespace_manager.bind('owl', rdflib.URIRef('http://www.w3.org/2002/07/owl#'))
    graph.namespace_manager.bind('rdfs', rdflib.URIRef('http://www.w3.org/2000/01/rdf-schema#'))
    graph.namespace_manager.bind('rdf', rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))

    # for s in graph.subjects(RDF + rdflib.URIRef('type'), OWL + rdflib.URIRef('Class')):
    #     print(s)

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

    def query_base_classes():
        class_list = Query.query_classes()
        base_classes = set()
        for cls in class_list:
            base_class = Query.query_base_class(cls)
            base_classes.add(base_class)
        return list(base_classes)

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

    def query_object_properties(sbol_class):
        query =     '''
            SELECT distinct ?sbol_property
            WHERE 
            {{
                ?sbol_property rdf:type owl:ObjectProperty .
                ?sbol_property rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* <{}>.
            }}
            '''.format(sbol_class)
        response = Query.graph.query(query)
        property_types = [str(row[0]) for row in response]
        return property_types

    def query_datatype_properties(sbol_class):
        query =     '''
            SELECT distinct ?sbol_property
            WHERE 
            {{
                ?sbol_property rdf:type owl:DatatypeProperty .
                ?sbol_property rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* <{}>.
            }}
            '''.format(sbol_class)
        response = Query.graph.query(query)
        property_types = [str(row[0]) for row in response]
        return property_types

    def query_property_datatype(sbol_property):
        # query =     '''
        #     SELECT distinct ?datatype
        #     WHERE 
        #     {{
        #         <{}> rdf:type owl:DatatypeProperty .
        #         <{}> rdfs:range ?datatype .
        #     }}
        #     '''.format(sbol_property)
        query =     '''
            SELECT distinct ?datatype
            WHERE 
            {{
                <{}> rdfs:range ?datatype .
            }}
            '''.format(sbol_property)
        response = Query.graph.query(query)
        datatypes = [str(row[0]) for row in response]
        return datatypes


    def query_property_name(sbol_property):
        query =     '''
            SELECT distinct ?sbol_property_name
            WHERE 
            {{
                ?sbol_property tawny:name ?sbol_property_name
            }}
            '''.format(sbol_property)    
        response = Query.graph.query(query)
        property_names = [str(row[0]) for row in response]
        return property_names

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

    def query_cardinality(sbol_property_name):
        query = '''
            SELECT distinct ?rdf_type
            WHERE 
            {{
                ?sbol_property rdf:type ?rdf_type .
                ?sbol_property tawny:name "{}"@en .
            }}
        '''.format(sbol_property_name)

        query = '''
            SELECT distinct ?rdf_type ?range
            WHERE 
            {{
                ?sbol_property rdf:type ?rdf_type .
                ?sbol_property tawny:name "{}"@en .
                ?restriction owl:onProperty ?sbol_property .
                ?restriction owl:someValuesFrom ?range
            }}
        '''.format(sbol_property_name)
        response = Query.graph.query(query)
        print('http://www.w3.org/2002/07/owl#FunctionalProperty' in response)

        property_type = [str(row[0]) for row in response]
        print('http://www.w3.org/2002/07/owl#FunctionalProperty' in property_type)
        return property_type


    def query_union():
        # query =     '''
        #     SELECT distinct ?union ?first ?rest
        #     WHERE 
        #     {
        #         ?union owl:unionOf ?collection .
        #         ?collection rdf:first ?first .
        #         ?collection rdf:rest* ?rest .
        #     }
        #     '''
        query =     '''
            SELECT ?p ?d
            WHERE {
              ?p rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* ?d
              filter isIri(?d)
            }
            '''
        response = Query.graph.query(query)
        property_types = [str(row[0]) for row in response]
        property_types = [row for row in response]

        return property_types

    # def query_properties(sbol_class):
    #     query =     '''
    #         SELECT distinct ?sbol_property_name
    #         WHERE 
    #         {{
    #             ?sbol_property rdf:type owl:ObjectProperty .
    #             ?sbol_property rdfs:domain ?o .
    #             ?o rdf:type owl:Class .
    #             ?sbol_property tawny:name ?sbol_property_name
    #         }}
    #         '''.format(sbol_class)
    #     response = Query.graph.query(query)
    #     property_types = [str(row[0]) for row in response]
    #     return property_types

    # def query_properties(sbol_class):
    #     query =     '''
    #         CONSTRUCT
    #         {
    #           ?s1 ?p1 ?o1 .           #-- internal edge in the path
    #           ?o1 ?p2 <sbol:> .           #-- final edge in the path
    #         }
    #         WHERE {
    #           sbol:role (<>|!<>)* ?s1 .     #-- start at :A and go any length into the path
    #           ?s1 ?p1 ?o1 .           #-- get the triple from within the path, but make
    #           ?o1 ?p2 <sbol:> .           #-- ?s2 that's related to an ?o2 by property :d .
    #         }
    #     '''

    #     # query =     '''
    #     #     CONSTRUCT { ?s ?p ?o }
    #     #     WHERE 
    #     #     {
    #     #         sbol:role (<>|!<>) ?s . 
    #     #         ?s ?p ?o .
    #     #     }
    #     #     '''

    #     # query =     '''
    #     #     CONSTRUCT { ?s ?p ?o }
    #     #     WHERE 
    #     #     {
    #     #         <http://sbols.org/v2#role> (<>|!<>)* ?s . 
    #     #         ?s ?p ?o .
    #     #     }
    #     #     '''
    #     response = Query.graph.query(query)
    #     for row in response:
    #         print(row)
    #     return([row for row in response])

# sbol_types = Query.query_toplevels()
# for sbol_type in sbol_types:
#     print(sbol_type)
#     property_types = Query.query_properties(sbol_type)
#     for property_type in property_types:
#         print('\t{}'.format(property_type))

# # Query and instantiate Identified and all subclasses
# sbol_types = Query.query_identified()
# for sbol_type in sbol_types:
#     # create_identified(sbol_type)
#     create_derived_classes(sbol_type)


# i = Identified('i')
# cd = ComponentDefinition('cd')
# print(cd.sequenceAnnotation)


