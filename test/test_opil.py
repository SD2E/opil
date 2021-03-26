from opil import *
from opil import __factory__
from sbol3 import set_namespace, TextProperty, Measure, Component, SBOL_TOP_LEVEL
from sbol_factory import ShaclValidator

from rdflib import Graph
import rdflib.compare
from math import inf
import unittest
import os
import json


MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
TEST_FILES = os.path.join(MODULE_LOCATION, 'test_files')

class TestOpil(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sbol.set_namespace('http://example.org')

    # def test_valid(self):
    #     doc = Document()
    #     p = ProtocolInterface('p')
    #     p.name = 'foo'
    #     doc.add(p)
    #     validation_report = doc.validate()
    #     self.assertTrue(validation_report.is_valid)

    # def test_invalid(self):
    #     # Parameters are forbidden to have more than one name
    #     doc = Document()
    #     protocol = ProtocolInterface('protocol')
    #     p = Parameter()
    #     p.__dict__['name'] = TextProperty(p, 'http://bioprotocols.org/opil/v1#name', 0, inf)
    #     p.name = ['foo', 'bar']
    #     protocol.has_parameter = [p]
    #     doc.add(protocol)
    #     validation_report = doc.validate()
    #     self.assertFalse(validation_report.is_valid)
    #     i_message = validation_report.results.find('Message: ') + 9
    #     message = validation_report.results[i_message:]
    #     self.assertEqual(validation_report.__repr__(), message)

    # def test_required_parameters(self):
    #     # Confirm that SHACL validation will catch the following rule:
    #     # A Parameter with required == True must have ParameterValue specified
    #     doc = Document()
    #     protocol = ProtocolInterface('protocol')
    #     p = Parameter()
    #     p.required = True
    #     protocol.has_parameter = [p]

    #     er = ExperimentalRequest('er')
    #     v = ParameterValue()
    #     er.has_parameter_value = [v]

    #     er.instance_of = protocol
    #     doc.add(protocol)
    #     doc.add(er)
    #     validation_report = doc.validate()
    #     self.assertFalse(validation_report.is_valid)

    #     v.value_of = p
    #     validation_report = doc.validate()
    #     self.assertTrue(validation_report.is_valid)

    # def test_top_level(self):
    #     # See issue 38
    #     doc = Document()
    #     protocol = ProtocolInterface('protocol')
    #     param = Parameter()
    #     doc.add(protocol)
    #     protocol.has_parameter = [param]
    #     object_ids = [o.identity for o in doc.objects]
    #     self.assertIn(protocol.identity, object_ids)
    #     self.assertNotIn(param.identity, object_ids)
    #     doc2 = Document()
    #     doc2.read_string(doc.write_string('nt'), 'nt')
    #     object_ids = [o.identity for o in doc2.objects]
    #     self.assertIn(protocol.identity, object_ids)

    #     # The following failed prior to resolution of 38
    #     self.assertNotIn(param.identity, object_ids)

    # def test_rdf_files(self):
    #     # In order for this to pass, the TestER graph needs to be merged
    #     # with the TimeSeries ProtocolInterface graph
    #     g = rdflib.Graph()
    #     g.parse(os.path.join(TEST_FILES, 'TestER.ttl'),
    #             format='ttl')
    #     validator = ShaclValidator()
    #     is_valid, g_results, results = validator.validate(g)
    #     self.assertTrue(is_valid)

    # def test_opil_files(self):
    #     doc = Document()
    #     doc.read(os.path.join(TEST_FILES, 'opil_output.xml'), 'xml')
    #     report = doc.validate()
    #     print(report.message)
    #     self.assertTrue(report.is_valid)

    # def test_growth_curve(self):
    #     with open(os.path.join(TEST_FILES, 'GrowthCurve.json')) as f:
    #         document_dict = json.load(f)
    #     protocol_params = document_dict['inputs']
    #     s = StrateosOpilGenerator()
    #     doc = s.parse_strateos_json('http://strateos.com',
    #                                      document_dict['name'], 
    #                                      document_dict['id'],
    #                                      document_dict['inputs'])
    #     report = doc.validate()
    #     self.assertTrue(report.is_valid)

    # def test_time_series(self):
    #     with open(os.path.join(TEST_FILES, 'TimeSeriesHTP.json')) as f:
    #         document_dict = json.load(f)
    #     s = StrateosOpilGenerator()
    #     doc = s.parse_strateos_json('http://strateos.com',
    #                                      document_dict['name'], 
    #                                      document_dict['id'],
    #                                      document_dict['inputs'])
    #     protocol = doc.find('http://strateos.com/TimeSeriesHTP')
    #     dotnames = []
    #     for param in protocol.has_parameter:
    #         dotnames.append(param.dotname)

    #     # Confirm that options that contain nested JSON objects are being handled
    #     self.assertIn('induction_info.induction_reagents.inducer_layout',
    #                   dotnames)

    #     # Confirm that multiple instances with the same dotname are not created, see #56
    #     # (These indicate correct handling of `options` objects in the JSON schema)
    #     self.assertEqual(dotnames.count(
    #                      'induction_info.induction_reagents.inducer_layout.inducer_unit'), 0)

    #     # Confirm that Strateos dotname encodes options syntax, see #76
    #     self.assertIn('induction_info.induction_reagents.inducer_layout.|.full_plate.inducer_unit',
    #                   dotnames)
    #     self.assertIn('induction_info.induction_reagents.inducer_layout.|.select_cols.inducer_unit',
    #                   dotnames)

    #     report = doc.validate()
    #     self.assertTrue(report.is_valid)

    # def test_obstacle_course(self):
    #     with open(os.path.join(TEST_FILES, 'ObstacleCourse.json')) as f:
    #         document_dict = json.load(f)
    #     s = StrateosOpilGenerator()
    #     doc = s.parse_strateos_json('http://strateos.com',
    #                                      document_dict['name'], 
    #                                      document_dict['id'],
    #                                      document_dict['inputs'])
    #     report = doc.validate()
    #     self.assertTrue(report.is_valid)
    #     for o in doc.objects:
    #         self.assertIn(SBOL_TOP_LEVEL, o._rdf_types)

    # def test_cell_free_bioswitches(self):
    #     with open(os.path.join(TEST_FILES, 'CellFreeRiboswitches.json')) as f:
    #         document_dict = json.load(f)
    #     s = StrateosOpilGenerator()
    #     doc = s.parse_strateos_json('http://strateos.com',
    #                                      document_dict['name'], 
    #                                      document_dict['id'],
    #                                      document_dict['inputs'])
    #     protocol = doc.find('http://strateos.com/CellFreeRiboswitches')
    #     report = doc.validate()
    #     self.assertTrue(report.is_valid)

    # def test_measurement(self):
    #     # Confirm functionality of Measurement and MeasurementType part of data model
    #     doc = Document()
    #     p = ProtocolInterface('p')
    #     mt = MeasurementType()
    #     p.protocol_measurement_type = [mt]
    #     mt.type = 'foo'
    #     e = ExperimentalRequest('e')
    #     m = Measurement()
    #     e.measurements = [m]
    #     m.instance_of = mt
    #     self.assertEqual(m.instance_of, mt.identity)
    #     self.assertEqual(type(mt.type), str)  # Confirm value is a string not list of characters
    #     mt.allowed_time = [TimeInterval()]
    #     mt.allowed_time.min_time = Measure(0, 'http://www.ontology-of-units-of-measure.org/resource/om-2#minute')
    #     mt.allowed_time.max_time = Measure(60,'http://www.ontology-of-units-of-measure.org/resource/om-2#minute')
    #     mt.minimum_interval = Measure(0.1, 'http://www.ontology-of-units-of-measure.org/resource/om-2#minute')
    #     m.time = [ Measure(50, 'http://www.ontology-of-units-of-measure.org/resource/om-2#minute') ]
    #     doc.add(e)
    #     doc.add(p)

    # def test_positional_arguments(self):
    #     # Some SBOL core classes have positional arguments in their constructor.
    #     # Instantiating OPIL subclasses of these was failing because OPIL did not
    #     # support positional arguments.
    #     # See issue #148
    #     doc = Document()
    #     template = Component('design', 'http://foo.org/bar')
    #     doc.add(template)

    #     # Confirm arbitrary arguments list (positional) and keywords work
    #     sample_space = SampleSet('conditions', template, name='foo')

    #     # Confirm keyword arguments work
    #     self.assertEqual(sample_space.name, 'foo')
    #     doc.add(sample_space)

    #     doc2 = Document()
    #     doc2.read_string(doc.write_string('turtle'), 'turtle')
    #     self.assertTrue(compare_documents(doc, doc2))

    # def test_is_top_level(self):
    #     self.assertTrue(__factory__.query.is_top_level('http://bioprotocols.org/opil/v1#SampleSet'))
    #     self.assertTrue(__factory__.query.is_top_level('http://sbols.org/v3#TopLevel'))
    #     self.assertFalse(__factory__.query.is_top_level('http://sbols.org/v3#Identified'))

    # def test_required(self):
    #     # Confirm that required arguments are propagated from super constructors, i.e., in this
    #     # example `template` is propagated from CombinatorialDerivation constructor.
    #     # Also, because this is a TopLevel, `identity` should be the first required argument
    #     required = __factory__.query.query_required_properties('http://bioprotocols.org/opil/v1#SampleSet')
    #     self.assertEqual(required, ['identity', 'template', 'replicates'])

    #     required = __factory__.query.query_required_properties('http://bioprotocols.org/opil/v1#EnumeratedValue')
    #     # non-TopLevel should not have identity as a required property
    #     self.assertNotIn('identity', required)

    #     # Because the superclass of EnumeratedValue, ParameterValue, also has a restriction
    #     # on `value_of` property, it was appearing twice in the list of required arguments
    #     self.assertNotEqual(required.count('value_of'), 2)

    def test_inheritance(self):
        sp = StringParameter()
        self.assertNotIn('http://bioprotocols.org/opil/v1#Parameter', sp._rdf_types)
        self.assertIn('http://bioprotocols.org/opil/v1#StringParameter', sp._rdf_types)
        self.assertEqual(len(sp._rdf_types), 2)
        template = Component('design', 'http://foo.org/bar')
        s = SampleSet('conditions', template)
        self.assertNotIn('http://sbols.org/v3#CombinatorialDerivation', s._rdf_types)
        self.assertIn('http://bioprotocols.org/opil/v1#SampleSet', s._rdf_types)
        self.assertEqual(len(s._rdf_types), 2)

def compare_documents(doc1, doc2):
    # Now compare the graphs in RDF
    g1 = doc1.graph()
    iso1 = rdflib.compare.to_isomorphic(g1)
    g2 = doc2.graph()
    iso2 = rdflib.compare.to_isomorphic(g2)
    rdf_diff = rdflib.compare.graph_diff(iso1, iso2)
    if rdf_diff[1] or rdf_diff[2]:
        print('Detected %d different RDF triples in %s' %
              (len(rdf_diff[1]) + len(rdf_diff[2]), test_path))
        for stmt in rdf_diff[1]:
            print('Only in original: %r', stmt)
        for stmt in rdf_diff[2]:
            print('Only in loaded: %r', stmt)
        print('Differences in RDF detected')
        return False
    return True

if __name__ == '__main__':
    unittest.main()
