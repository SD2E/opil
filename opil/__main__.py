from .uml_factory import Query
from .opil_factory import OPILFactory

import argparse
import os


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--input",
    help="Input ontology",
)
parser.add_argument(
    "-o",
    "--output",
    help="Output path for files"
)

# Generate a dictionary from the command-line arguments
args_dict = vars(parser.parse_args())

# Import ontology
default_ontology = f'{MODULE_PATH}/rdf/opil.ttl'
with open(default_ontology, 'r') as o:
    for r in o:
        print(r)

# Print data model
print(OPILFactory.__doc__)

# Generate documentation
if args_dict['output']:
    OUTPUT_PATH = args_dict['output']
    if not os.path.exists(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)
    #for class_uri in Query.query_classes():
        #class_name = sbol.utils.parse_class_name(class_uri)
        #dot = graphviz.Digraph(class_name)
        ## dot.graph_attr['splines'] = 'ortho'
        #OPILFactory.generate(class_uri, OPILFactory.draw_class_definition, dot)
        ## OPILFactory.generate(class_uri, OPILFactory.draw_abstraction_hierarchy, dot)
        #source = graphviz.Source(dot.source.replace('\\\\', '\\'))
        ## source.render(f'./uml/{class_name}_definition_and_abstraction')
        #source.render(f'{OUTPUT_PATH}/{class_name}')


