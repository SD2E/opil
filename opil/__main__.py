from .opil_factory import OPILFactory
from .uml_factory import UMLFactory
from .query import Query
import argparse
import posixpath
import os


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--input",
    help="Input ontology",
)
parser.add_argument(
    "-n",
    "--namespace",
    help="Ontology namespace",
)
parser.add_argument(
    "-d",
    "--documentation",
    help="Output directory for UML"
)

# Generate a dictionary from the command-line arguments
args_dict = vars(parser.parse_args())
if args_dict['input'] and not args_dict['namespace']:
    raise Exception('If specifying an input ontology, a namespace must also be specified')

# Import ontology
default_ontology = posixpath.join(MODULE_PATH, 'rdf/opil.ttl')
opil_path = posixpath.join(os.path.dirname(os.path.realpath(__file__)), 'rdf/opil.ttl')
if not args_dict['input']:
    opil_factory = OPILFactory(opil_path, Query.OPIL, verbose=True)
else:
    opil_factory = OPILFactory(args_dict['input'], args_dict['namespace'], verbose=True)

# Generate documentation
if args_dict['documentation']:
    OUTPUT_PATH = args_dict['documentation']
    if not os.path.exists(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)
    UMLFactory(opil_factory)

