# This script parses an SBOL file and produces a Provenance Graph for it using Graphviz
# This is specifically for the PROV-O model that SBOL uses
# USAGE: Simply pass an SBOL file as an argument when running this script

from graphviz import Digraph, Source

dot = Digraph('digraph')

node_format = {
                'label' : None,
                'fontname' : 'Bitstream Vera Sans',
                'fontsize' : '8',
                'shape': 'record'
}

inheritance_relationship = {
                'arrowhead' : 'empty',
                'fontname' : 'Bitstream Vera Sans',
                'fontsize' : '8',
}
composition_relationship = {
                'arrowhead' : 'diamond',
                'fontname' : 'Bitstream Vera Sans',
                'fontsize' : '8',
}
association_relationship = {
                'arrowhead' : 'odiamond',
                'fontname' : 'Bitstream Vera Sans',
                'fontsize' : '8',
                'dir' : 'both'
}
node_format['label'] = '{Animal|+ name : string\l+ age : int\l|+ die() : void\l}'
dot.node('Foo', **node_format)
dot.node('Bar', **node_format)
dot.edge('Foo', 'Bar', **association_relationship)
source = Source(dot.source.replace('\\\\', '\\'))
print(source.source)

source.render('foo', view=True) # Create the graph image
