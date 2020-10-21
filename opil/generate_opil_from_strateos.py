import argparse
import json
import sbol3
import opil

# Map of unit names to om:Unit instance IRIs
UNITS = {
    'microliter': 'http://www.ontology-of-units-of-measure.org/resource/om-2/microlitre',
    'nanometer' : 'http://www.ontology-of-units-of-measure.org/resource/om-2/nanometre',
    'hour' : 'http://www.ontology-of-units-of-measure.org/resource/om-2/hour'
}


class StrateosOpilGenerator():
    '''
    This class shows how OPIL can be generated from a Strateos protocol
    JSON schema. An OPIL representation of a Strateos protocol is
    essentially just a collection of parameters. The opil:name property
    is used for the parameter so-called dotnames.
    '''

    def __init__(self):
        pass

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-i",
            "--input",
            dest="in_file",
            help="Input JSON file",
            default='/Users/rmarkelo/Documents/BBN/SD2/time_series_schema.json'
        )
        parser.add_argument(
            "-o",
            "--output",
            dest="out_file",
            help="Output OPIL Turtle file",
            default='TimeSeriesHTC.nt'
        )
        parser.add_argument(
            "-n",
            "--namespace",
            dest="namespace",
            help="Namespace for output file",
            default='http://strateos.com/'
        )
        parser.add_argument(
            "-p",
            "--protocol",
            dest="protocol_name",
            help="Protocol name",
            default='TimeSeriesHTC'
        )

        # Generate a dictionary from the command-line arguments
        args_dict = vars(parser.parse_args())

        # Get contents of JSON file
        with open(args_dict['in_file']) as f:
            document_dict = json.load(f)

        # Parse the JSON and return a SBOL document
        print('Generating OPIL from JSON file ', args_dict['in_file'])
        document = self.parse_strateos_json(args_dict['namespace'],
                                            args_dict['protocol_name'], document_dict)

        # Write out the document to a file
        document.bind('opil', opil.Query.OPIL)  # Set namespace prefix

        # Use Ntriples serialization to avoid rdflib issue with literal
        # data types that occurs with Turtle serialization
        document.write(args_dict['out_file'], file_format='nt')

    def parse_strateos_json(self, namespace, protocol_name, document_dict):
        # Set the namespace for created instances
        sbol3.set_namespace(namespace)

        # Create the ProtocolInterface instance
        self.protocol = opil.ProtocolInterface(protocol_name)
        self.protocol.name = protocol_name

        # Create the document and add the ProtocolInterface to it
        self.doc = sbol3.Document()
        self.doc.add(self.protocol)

        # Create a list of Parameters
        self.param_list = []

        # Iterate through the top-level JSON objects and add Parameters to the list
        for section_name in document_dict:
            section_dict = document_dict[section_name]

            # Parameters are found in 'inputs' JSON objects
            if 'inputs' in section_dict:
                inputs_dict = section_dict['inputs']
                for param_name in inputs_dict:

                    # The 'type' value indicates what Parameter subclass should be used.
                    # Form the Strateos dotname from the section name and parameter name
                    type = inputs_dict[param_name]['type']
                    self.handle_type(type, param_name, inputs_dict[param_name],
                                     section_name + '.' + param_name)

        # Add parameters to ProtocolInterface
        self.protocol.has_parameter = self.param_list

        return self.doc

    def handle_type(self, type, id_string, param_dict, dotname):
        '''
        The handle_type method selects the method for parsing the parameter JSON object
        based on its type field
        '''
        method = StrateosOpilGenerator.type_handlers[type]
        method(self, id_string, param_dict, dotname)

    def handle_choice(self, id_string, param_dict, dotname):
        '''
        Choice type maps to Enumerated parameters
        '''
        param = opil.EnumeratedParameter(id_string)
        param.name = dotname
        options_list = param_dict['options']
        allowed_values = []
        for option in options_list:
            allowed_values.append(option['value'])
        param.allowed_value = allowed_values
        if 'required' in param_dict:
            param.required = True
        self.param_list.append(param)

    def handle_string(self, id_string, param_dict, dotname):
        param = opil.StringParameter(id_string)
        param.name = dotname
        if 'default' in param_dict:
            default = opil.StringValue(id_string + '_default')
            default.value = param_dict['default']
            param.default_value = [default]
            self.doc.add(default)
        if 'required' in param_dict:
            param.required = True
        self.param_list.append(param)

    def handle_integer(self, id_string, param_dict, dotname):
        param = opil.IntegerParameter(id_string)
        param.name = dotname
        if 'default' in param_dict:
            default = opil.IntegerValue(id_string + '_default')
            default.value = param_dict['default']
            param.default_value = [default]
            self.doc.add(default)
        if 'required' in param_dict:
            param.required = True
        self.param_list.append(param)

    def handle_measure(self, id_string, param_dict, dotname):
        '''
        Volume, length, and time types map to MeasureParameters
        Default values are MeasureValue instances with om:Measure
        instances carrying the numerical values and units
        '''
        param = opil.MeasureParameter(id_string)
        param.name = dotname
        if 'default' in param_dict:
            default_instance = opil.MeasureValue(id_string + '_default')
            default_value = param_dict['default']
            if isinstance(default_value, str):

                # Parse the string to get a number and unit name
                string_splits = param_dict['default'].split(':')
                value = float(string_splits[0])
                unit_iri = UNITS[string_splits[1]]
            else:

                # If the default value is a number, not a string,
                # then use the opil:pureNumber Unit instance
                value = default_value
                unit_iri = 'http://bbn.com/synbio/opil#pureNumber'
            measure_name = id_string + '_default_measure'
            measure = sbol3.Measure(value, unit_iri, name=measure_name)
            default_instance.has_measure = measure
            param.default_value = [default_instance]
            self.doc.add(default_instance)
        if 'required' in param_dict:
            param.required = True
        self.param_list.append(param)

    def handle_bool(self, id_string, param_dict, dotname):
        param = opil.BooleanParameter(id_string)
        param.name = dotname
        if 'default' in param_dict:
            default = opil.BooleanValue(id_string + '_default')
            default.value = param_dict['default']
            param.default_value = [default]
            self.doc.add(default)
        if 'required' in param_dict:
            param.required = True
        self.param_list.append(param)

    def handle_group(self, id_string, param_dict, dotname):
        '''
        The group type is basically just a container for other
        input types
        '''
        if 'inputs' in param_dict:
            inputs_dict = param_dict['inputs']
            for key in inputs_dict:
                type = inputs_dict[key]['type']
                self.handle_type(type, key, inputs_dict[key], dotname + '.' + key)

    def handle_group_choice(self, id_string, param_dict, dotname):
        '''
        The group-choice type contains an 'options' list of parameters
        '''
        if 'options' in param_dict:
             dict_list = param_dict['options']
             for dict in dict_list:
                inputs_dict = dict['inputs']
                for key in inputs_dict:
                    param_dict = inputs_dict[key]
                    type = param_dict['type']
                    self.handle_type(type, key, param_dict, dotname + '.' + key)

    # Mappings of JSON object types to methods. Not that aliquot and aliquot+ types
    # become string parameters
    type_handlers = {'choice': handle_choice, 'string': handle_string,
                     'volume': handle_measure, 'time': handle_measure,
                     'length': handle_measure, 'decimal': handle_measure,
                     'bool': handle_bool, 'group': handle_group,
                     'group+': handle_group, 'group-choice': handle_group_choice,
                     'integer': handle_integer,
                     'aliquot': handle_string, 'aliquot+': handle_string}

if __name__ == "__main__":
    opil_generator = StrateosOpilGenerator()
    opil_generator.main()
