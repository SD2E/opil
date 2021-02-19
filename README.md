# opil

![opil](https://github.com/sd2e/opil/workflows/opil/badge.svg?branch=github_actions_ci)

The Open Protocol Interface Language (OPIL) is intended as a standard data model for protocol interfaces. This repository represents an initial OPIL implementation. 

## Installation
The  `opil` package and its dependencies can be installed with
```
pip install opil
```
Python 3 only is supported.

## OPIL API

The OPIL module is an extension of the underlying [pySBOL](https://github.com/SynBioDex/pySBOL3) module. Users who are familiar with pySBOL will find that the OPIL API follows all the same patterns.

Import as follows:

```
import opil
```

The OPIL data model is encoded as an ontology using the Web Ontology Language (OWL). (A Turtle serialization of the OPIL ontology can be found in the 'rdf' directory.) The module's API is dynamically generated directly from this OWL specification immediately upon import of the module into the user's Python environment. The ontology specifies the Python classes, their attributes, their types, and their cardinality.

## Working with OPIL Documents

All file I/O is handled through a `Document` object. In the following example, we read a file that describes a protocol interface for a time series experiment. The `file_format` can be `ttl` (Turtle), `xml` (RDF-XML), and `nt` (N-Triples) 

```
doc = opil.Document()
doc.read('TimeSeriesHTC.ttl', file_format='ttl')
```

Once a `Document` is loaded, you can inspect its contents as follows:

```
for obj in doc.objects:
    print(obj.name)
    print(type(obj))
    print(obj.identity)
    print()
```

The `name` attribute is used for human-readable and/or lab-specific identifiers. The `identity` attribute specifies the unique Uniform Resource Identifier (URI) for each object. The URI is used to retrieve specific objects from the Document.

```
protocol = doc.find('http://strateos.com/TimeSeriesHTC')
```

## Creating objects

Every OPIL object is identified by a unique URI. When a new object is created, the URI for an object is automatically generated. Every constructor for an OPIL object takes a single argument which is its local ID. The full URI is then generated from a namespace and the local ID. This local ID must consist of only alphanumeric characters and/or underscores.

When constructing a new `Document`, the general workflow is as follows. First, set the namespace that governs new objects. Second, create new objects. Finally, add the new object to the `Document`.  For example:

```
set_namespace('http://bbn.com/synbio/')
doc = Document()
protocol = ProtocolInterface('TimeSeries')
doc.add(protocol)
```

## Validation

A `Document` can be validated as follows:

```
validation_report = doc.validate()
print(validation_report)
```

This returns a `ValidationReport` object which has a boolean status field, `is_valid`, that indicates whether the `Document` is valid, and a `message` field which provides a text description of any validation issues that were identified.

## Running OPIL as an executable

The opil module can also be run as an executable. This provides options for displaying a summary of the data model, generating UML figures for documentation, and for prototyping data models from arbitrary ontologies besides OPIL.

The basic pattern for using OPIL as an executable is as follows: 
```
python3 -m opil
```

This can be followed by additional flags as follows:
```
usage: -m [-h] [-i INPUT] [-n NAMESPACE] [-d DOCUMENTATION] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input ontology
  -n NAMESPACE, --namespace NAMESPACE
                        Ontology namespace
  -d DOCUMENTATION, --documentation DOCUMENTATION
                        Output directory for UML
  -v, --verbose         Print data model as it is generated
```

Verbose mode displays a summary of the data model. This lists each class, its properties, their datatype, and lower and upper cardinalities, as shown below.

```
MeasurementType
---------------
	allowed_time	TimeInterval	0	inf
	min_interval	Measure	0	1
	max_count	integer	0	1
	type	anyURI	1	1
	min_count	integer	0	1
	required	boolean	1	1
```

### Working with arbitrary ontologies

To work with arbitrary ontologies, both a file and namespace for the ontology must be provided. For example, the following usage will input the PAML ontology, display a visual summary, and generate UML diagrams in a directory called `uml`:

```
python3 -m opil -i ../paml/paml.ttl -n http://bioprotocols.org/paml# -d uml -v
```
