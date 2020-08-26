import json
from decimal import Decimal

from rdflib import Graph

class OpilJsonGenerator:
        '''This class shows how JSON can be generated from an RDF
        representation of an experimental request using the OPIL ontology. 
        The current example is the YeastSTATES 1.0 Time Series Round 1 request.  
        Only part of the first row of the structured request table from this
        document is currently represent as RDF'''

        def main(self):

            g = Graph()

            # Load RDF files
            print('Loading RDF files...')
            g.parse('rdf/sbol3.ttl', format='ttl')
            g.parse('rdf/opil.ttl', format='ttl')
            g.parse('rdf/TimeSeriesProtocol.ttl', format='ttl')
            g.parse('rdf/YeastSTATES_1.0_Time_Series_Round_1.ttl', format='ttl')
            g.parse('rdf/om-2.0.rdf')

            # Load the various SPARQL queries
            ss_query = self.load_sparql('sparql/sampleSet.sparql')
            m_t_query = self.load_sparql('sparql/measurementType.sparql')
            rep_query = self.load_sparql('sparql/replicates.sparql')
            var_comp_query = self.load_sparql('sparql/variableComponents.sparql')
            variants_query = self.load_sparql('sparql/variants.sparql')
            timepoints_query = self.load_sparql('sparql/timepoints.sparql')
            
             # Execute SPARQL query to find all sample sets
            sample_set_iris = []
            for row in g.query(ss_query):
                sample_set_iris.append(row.ss)

            # Generate the JSON
            print('Generating JSON...')
            experimental_request = {'runs' : []}
            measurements = []
            for ss_iri in sample_set_iris:
                sample_set_dict = {}

                # Get measurement type for this sample set. Measurement types
                # are labels for the MeasurementType instances in the protocol
                # definition that correspond to the measurements for this sample set
                query = m_t_query.format(iri=ss_iri)
                for row in g.query(query):
                    sample_set_dict.update({'measurement_type': row.type.value})

                # Get number of replicates for this sample set
                query = rep_query.format(iri=ss_iri)
                for row in g.query(query):
                    sample_set_dict.update({'replicates': row.rep.value})

                # Get all VariableComponents for this SampleSet
                var_comp_iris = []
                query = var_comp_query.format(iri=ss_iri)
                for row in g.query(query):
                    var_comp_iris.append(row.varComp)

                # Get all variants for each VariableComponent
                for vc_iri in var_comp_iris:
                    query = variants_query.format(iri=vc_iri)
                    numerical_values_and_units = {}
                    value = None
                    strains = []
                    for row in g.query(query):
                        variantName = row.label.value
                        if not row.numericalValue is None:
                            if type(row.numericalValue.value) == Decimal:
                                numerical_value = float(row.numericalValue.value)
                            else:
                                numerical_value = row.numericalValue.value
                            numerical_values_and_units.update({'value': numerical_value, 'unit': row.unitName.value})
                        elif not row.varValue is None:
                            value = row.varValue.value
                            sample_set_dict.update({variantName: value})
                        else:
                            strains.append(str(row.var))

					# Variants can have values (e.g. replicates have numbers) or
					# they can have measures with values and units (e.g. temperatures) or
					# they are stand alone individuals (e.g. strains)
                    if value is None:
                        if not numerical_values_and_units:
                            sample_set_dict.update({variantName: strains})
                        else:
                            sample_set_dict.update({variantName: numerical_values_and_units})

                # Get the timepoints for this SampleSet's Measurement
                query = timepoints_query.format(iri=ss_iri)
                timepoints = []
                for row in g.query(query):
                    numerical_value = float(row.value.value)
                    timepoint_dict = {'value': numerical_value, 'unit': row.unitName.value}
                    timepoints.append(timepoint_dict)

                sample_set_dict.update({'timepoints': timepoints})
                measurements.append(sample_set_dict)

            experimental_request.get('runs').append({'measurements': measurements})
            print(json.dumps(experimental_request, indent=4, sort_keys=False))

        def load_sparql(self, file_path):
            with open(file_path, 'r') as query_file:
                # Strip newline characters and concatenate lines
                query = ' '.join([line.strip() for line in query_file])
            return query

if __name__ == "__main__":
    json_generator = OpilJsonGenerator()
    json_generator.main()