from opil_factory import *

opil_types = Query.query_base_classes()
for opil_type in opil_types:
    OPILFactory.create_base_class(opil_type)
    OPILFactory.create_derived_classes(opil_type)

# for opil_type in opil_types:
#     opil_properties = Query.query_datatype_properties(opil_type)
#     for opil_property in opil_properties:
#         datatype = Query.query_property_datatype(opil_property)
#         print(opil_type, opil_property, datatype)

# for opil_type in opil_types:
#     opil_properties = Query.query_object_properties(opil_type)
#     for opil_property in opil_properties:
#         datatype = Query.query_property_datatype(opil_property)
#         print(opil_type, opil_property, datatype)

from opil_factory import *

p = Protocol('foo')
print(p.type_uri)
er1 = ExperimentalRequest('foo')
er2 = ExperimentalRequest('foo')
print(dir(er1))

    # property_types = Query.query_properties(sbol_type)
    # for property_type in property_types:
    #     property_name = Query.query_property_name(property_type)
    #     print(f'\t{property_name}')
    #     # cardinality = Query.query_cardinality(property_type)
    #     # print(f'\t{property_name}\t{cardinality}')

# from sbol_owl import ComponentDefinition

# i = Identified('i')
# cd = ComponentDefinition('cd')
# print(cd.sequenceAnnotation)


# q=Query(file)
# print(Query.query_union())