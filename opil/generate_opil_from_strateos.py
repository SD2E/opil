import argparse
import json
import sbol3
from sbol3 import Measure, om_unit
import opil


class StrateosOpilGenerator():
    '''
    This class shows how OPIL can be generated from a
    Strateos protocol JSON schema
    '''

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
            default='TimSeriesHTC.ttl'
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

        # Generate a dict from the command-line arguments
        args_dict = vars(parser.parse_args())

        # Get contents of JSON file
        with open(args_dict['in_file']) as f:
            document_dict = json.load(f)

        type_list = ['choice', 'string', 'volume', 'time', 'length', 'bool']

        # Skip the experimental_info section - these parameters are in the SD2 ontology
        section_list = ['exp_info', 'inoc_info', 'recovery_info', 'induction_info',
                        'plate_reader_info', 'run_info', 'validate_samples']

        # Set the namespace for created instances
        sbol3.set_homespace(args_dict['namespace'])

        # Create the ProtocolInterface instance
        self.protocol = opil.Protocol(args_dict['protocol_name'])
        self.protocol.name = args_dict['protocol_name']

        # Create a list of Parmeters
        self.param_list = []

        # Create the document
        self.doc = sbol3.Document()
        self.doc.add(self.protocol)

        for section in document_dict:
            if section in section_list:
                section_dict = document_dict[section]
                if 'inputs' in section_dict:
                    inputs_dict = section_dict['inputs']
                    for param in inputs_dict:
                        type = inputs_dict[param]['type']
                        if type in type_list:
                            self.handle_type(type, param, inputs_dict[param])

        # Add parameters to ProtocolInterface
        self.protocol.has_parameter = self.param_list

        # Write out to a file
        self.doc.write(args_dict['out_file'], file_format='ttl')

    def handle_choice(self, id_string, param_dict):
        pass

    def handle_string(self, id_string, param_dict):
        param = opil.StringParameter(id_string)
        param.name = param_dict['label']
        if 'default' in param_dict:
            default = opil.StringValue(id_string + '_default')
            default.value = param_dict['default']
            param.default_value = [default]
            self.doc.add(default)
        self.param_list.append(param)

    def handle_volume(self, id_string, param_dict):
        param = opil.MeasureParameter(id_string)
        param.name = param_dict['label']
        if 'default' in param_dict:
            default = opil.MeasureValue(id_string + '_default')
            measure = om_unit.build_measure(id_string + '_default_measure')
            measure.value = 42
            default.has_value_object = [measure]
            param.default_value = [default]
            self.doc.add(default)
        self.param_list.append(param)


    def handle_time(self, id_string, param_dict):
        pass

    def handle_length(self, id_string, param_dict):
        pass

    def handle_bool(self, id_string, param_dict):
        param = opil.BooleanParameter(id_string)
        param.name = param_dict['label']
        if 'default' in param_dict:
            default = opil.BooleanValue(id_string + '_default')
            default.value = param_dict['default']
            param.default_value = [default]
            self.doc.add(default)
        self.param_list.append(param)

    type_handlers = {'choice': handle_choice, 'string': handle_string,
                     'volume': handle_volume, 'time': handle_time,
                     'length': handle_length, 'bool': handle_bool}

    def handle_type(self, type, id_string, param_dict):
        method = StrateosOpilGenerator.type_handlers[type]
        method(self, id_string, param_dict)


if __name__ == "__main__":
    opil_generator = StrateosOpilGenerator()
    opil_generator.main()
