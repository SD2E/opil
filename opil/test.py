from graphviz import Digraph
d=Digraph()
d.node('test',label='line 1\nline 2')
print(d.source)
