#!/usr/bin/python
import sys
import debby as db
g1 = db.debruijn_graph.load(sys.argv[1])

#for i in range(g1.num_edges): print g1.label(g1._edge_to_node(i)) + g1._edges[i]

for i in range(g1.num_edges): print g1.edge_label(i)
