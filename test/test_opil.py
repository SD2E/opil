from opil import *
from sbol3 import TextProperty
from math import inf
import unittest

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
