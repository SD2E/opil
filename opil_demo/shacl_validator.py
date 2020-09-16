from rdflib import Graph
from pyshacl import validate

class ShaclValidator:

    def main(self):

        # Load Turtle files into a RDF graph
        print('Loading RDF files...')
        g = Graph()
        g.parse('rdf/sbol3.ttl', format='ttl')
        g.parse('rdf/opil.ttl', format='ttl')
        g.parse('rdf/sd2.ttl', format='ttl')
        g.parse('rdf/TimeSeriesProtocol.ttl', format='ttl')
        g.parse('rdf/YeastSTATES_1.0_Time_Series_Round_1.ttl', format='ttl')
        g.parse('rdf/om-2.0.rdf')
        g.parse('rdf/opil-shacl.shapes.ttl', format='ttl')

        # Do the validation
        print('Validating experimental requests...')
        r = validate(g, shacl_graph=None, ont_graph=None, inference='rdfs',
                     abort_on_error=False, meta_shacl=False,
                     advanced=True, debug=False)
        conforms, results_graph, results_text = r
        print(results_text)

if __name__ == "__main__":
    validator = ShaclValidator()
    validator.main()