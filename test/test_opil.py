from opil import *
from sbol3 import TextProperty
import rdflib

from math import inf
import unittest
import os
import json

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
TEST_FILES = os.path.join(MODULE_LOCATION, 'test_files')

class TestOpil(unittest.TestCase):

    def test_valid(self):
        doc = Document()
        p = Parameter('p')
        p.name = 'foo'
        doc.add(p)
        validation_report = doc.validate()
        self.assertTrue(validation_report.is_valid)

    def test_invalid(self):
        # Parameters are forbidden to have more than one name
        doc = Document()
        p = Parameter('p')
        p.__dict__['name'] = TextProperty(p, 'http://bbn.com/synbio/opil#name', 0, inf)
        p.name = ['foo', 'bar']
        doc.add(p)
        validation_report = doc.validate()
        self.assertFalse(validation_report.is_valid)
        i_message = validation_report.results.find('Message: ') + 9
        message = validation_report.results[i_message:]
        self.assertEqual(validation_report.__repr__(), message)

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
    #         dotnames.append(param.name)
    #     # Confirm that multiple instances with the same dotname are created.
    #     # (These indicate correct handling of `options` objects in the JSON schema)
    #     self.assertEqual(dotnames.count(
    #                      'induction_info.induction_reagents.inducer_layout.inducer_unit'), 2)

    #     # Confirm that options that contain nested JSON objects are being handled
    #     self.assertIn('induction_info.induction_reagents.inducer_layout',
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
