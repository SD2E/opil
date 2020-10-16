# opil
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

The OPIL data model is encoded as an ontology using the Web Ontology Language (OWL). (A Turtle serialization of the OPIL ontology can be found in the 'rdf' directory.) The module's API is dynamically generated directly from this OWL specification immediately upon import of the module into the user's Python environment. The ontology specifies the Python classes, their attributes, their types, and their cardinality. The user can print details of the data model as follows:

```
opil.help()
```

This will list the classes, their attributes, and their types. 

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
