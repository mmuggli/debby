#!/usr/bin/python
import sys
import debby as db
g1 = db.debruijn_graph.load(sys.argv[1])
g2 = db.debruijn_graph.load(sys.argv[2])

#for i in range(g1.num_edges): print g1.label(g1._edge_to_node(i)) + g1._edges[i]
assert g1.k == g2.k

def get_column(g, col_num):
    column = []
    for i in range(g.num_edges):
        if col_num == 0:
            column.append(g._edges[i][0])
        else:
            for j in range(col_num - 1):
                i = g1._bwd(i)
            column.append(g._F_inv(i))
    return column

def set_iter(sets):
    assert sets[-1] == 1
    end = sets.index(1)
    start = 0
    while end != len(sets) - 1:
        yield sets[start:end+1]
        start = end + 1
        end = sets.index(1, start)
    yield sets[start:]
            
def subdivide(g1_subcol, g2_subcol):
    active_alphabet = sorted(list(set(g1_subcol) & set(g2_subcol)))
    assert len(active_alphabet) > 0
    g1_out = []
    g2_out = []
    for letter in active_alphabet:
        g1_out += [0] * g1_subcol.count(letter) + [1]
        g2_out += [0] * g2_subcol.count(letter) + [1]        
    return g1_out, g2_out
        
    # g1_pref_class = g1_col[0]
    # g2_pref_class = g2_col[0]
    # if g1_pref_class == g2_pref_class:
    #     while g1_col[g1_ptr] == g1_pref_class:
    #         g1_out_set.append(0)
    #         g1_ptr += 1
    #     g1_out_set.append(1)
    #     while g2_col[g2_ptr] == g2_pref_class:
    #         g2_out_set.append(0)
    #         g2_ptr += 1
    #     g2_out_set.append(1)
    

def refine_sets(g1_col, g2_col, g1_sets, g2_sets):
    g1_out_set = []
    g2_out_set = []
    g1_ptr = 0
    g2_ptr = 0
    
    for g1_set, g2_set in zip(set_iter(g1_sets), set_iter(g2_sets)):
        g1_num = len(g1_set) - 1
        g2_num = len(g2_set) - 1
        g1_subsets, g2_subsets = subdivide(g1_col[g1_ptr:g1_ptr+g1_num],
                                           g2_col[g2_ptr:g2_ptr+g2_num])
        assert g1_subsets.count(1) > 0
        assert g2_subsets.count(1) > 0
        g1_out_set += g1_subsets
        g2_out_set += g2_subsets
        g1_ptr += g1_num
        g2_ptr += g2_num
    return g1_out_set, g2_out_set
        
    
            
# main merge

# initialize sets to put all elements in the same equivalence class
# sets are contiguous runs of 0's which each indicate that for each rank_0 element,
# the corresponding element of BWT appears to be included in that set (so far)
g1_sets = [0] * g1.num_edges + [1]
g2_sets = [0] * g2.num_edges + [1]
            
for colno, col in enumerate([i + 1 for i in range(g1.k)] + [0]):
    print "doing column", colno, "g1 count:", g1_sets.count(1), "g2 count:", g2_sets.count(1)
    g1_col = get_column(g1, col)
    g2_col = get_column(g2, col)
    g1_sets, g2_sets = refine_sets(g1_col, g2_col, g1_sets, g2_sets)

g1_ptr = 0
g2_ptr = 0
for g1_set, g2_set in zip(set_iter(g1_sets), set_iter(g2_sets)):
    if g1_set[0] == 0:
        print g1._edges[g1_ptr]
        g1_ptr += 1
        if g2_set[0] == 0:
            g2_ptr += 1
    else:
        print g2_edges[g2_ptr]
        g2_ptr += 1
