#!/usr/bin/python
import sys
import debby as db
g1 = db.debruijn_graph.load(sys.argv[1])
col_num = int(sys.argv[2])

#for i in range(g1.num_edges): print g1.label(g1._edge_to_node(i)) + g1._edges[i]

for i in range(g1.num_edges):
    if col_num == 0:
        print (g1._edges[i][0])
    else:
        for j in range(col_num - 1):
            i = g1._bwd(i)
        print (g1._F_inv(i))
print "-------"
for i in range(g1.num_edges):
    if col_num == 0:
        print (g1._edges[i][0])
    else:
        for j in range(col_num - 1):
            i = g1._bwd(i)
        print (g1._F_inv(i))
        
