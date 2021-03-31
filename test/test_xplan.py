from opil import *
from opil import __factory__
from opil import __xplan_factory__
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

class TestXplan(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sbol.set_namespace('http://example.org')

    def test_required_parameters(self):
        # Confirm that SHACL validation will catch the following rule:
        # A Parameter with required == True must have ParameterValue specified
        doc = Document()
        protocol = ProtocolInterface('protocol')
        p = Parameter()
        p.required = True
        protocol.has_parameter = [p]

        er = ExperimentalRequest('er')
        v = ParameterValue()
        er.has_parameter_value = [v]

        er.instance_of = protocol

        xp = XPlanRequest('xp')

        doc.add(xp)
        doc.add(protocol)
        doc.add(er)
        validation_report = doc.validate()
        self.assertFalse(validation_report.is_valid)

        v.value_of = p
        validation_report = doc.validate()
        self.assertTrue(validation_report.is_valid)


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
