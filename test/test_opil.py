from opil import *
from sbol3 import TextProperty
import rdflib
from math import inf
import unittest
import os


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

    def test_rdf_files(self):
        # In order for this to pass, the TestER graph needs to be merged
        # with the TimeSeries ProtocolInterface graph
        g = rdflib.Graph()
        g.parse(os.path.join(TEST_FILES, 'TestER.ttl'),
                format='ttl')
        validator = ShaclValidator()
        is_valid, g_results, results = validator.validate(g)
        self.assertTrue(is_valid)

    def test_opil_files(self):
        doc = Document()
        doc.read(os.path.join(TEST_FILES, 'opil_output.xml'), 'xml')
        report = doc.validate()
        self.assertTrue(report.is_valid)
