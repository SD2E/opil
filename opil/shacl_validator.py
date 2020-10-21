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
        #g.parse('rdf/TimeSeriesProtocol.ttl', format='ttl')
        g.parse('../TimeSeriesHTC.ttl', format='ttl')
        #g.parse('rdf/YeastSTATES_1.0_Time_Series_Round_1.ttl', format='ttl')
        g.parse('rdf/om-2.0.rdf')
        g.parse('rdf/opil-shacl.shapes.ttl', format='ttl')
        g.parse('rdf/TestER.ttl', format='ttl')

        # Do the validation
        print('Validating graph...')
        conforms, results_graph, results_text = \
            validate(g, shacl_graph=None, ont_graph=None, inference='rdfs',
                     abort_on_error=False, meta_shacl=False,
                     advanced=True, debug=False)

        if conforms:
            print('Graph is valid')
        else:
            print('Graph is invalid:\n')
            print(results_text)

        # Query the results graph to find the problem instances
        # bad_things_query = self.load_sparql('sparql/badInstances.sparql')
        # query_results = results_graph.query(bad_things_query)

        # if query_results:
            # for row in query_results:
            #     print('{}: {}'.format(row.msg.value, row.bad))

    def load_sparql(self, file_path):
        with open(file_path, 'r') as query_file:
            # Strip newline characters and concatenate lines
            query = ' '.join([line.strip() for line in query_file])
        return query

if __name__ == "__main__":
    validator = ShaclValidator()
    validator.main()