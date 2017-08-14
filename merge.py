#!/usr/bin/python
import sys
import debby as db
g1 = db.debruijn_graph.load(sys.argv[1])
g2 = db.debruijn_graph.load(sys.argv[2])

#for i in range(g1.num_edges): print g1.label(g1._edge_to_node(i)) + g1._edges[i]
assert g1.k == g2.k

# counts W as col_num == -1
def get_column(g, col_num):
    column = []
    for i in range(g.num_edges):
        if col_num == 0:
            column.append(g._edges[i][0])
        else:
            for j in range(col_num - 1):
                i = g._bwd(i)
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
    active_alphabet = sorted(list(set(g1_subcol) | set(g2_subcol)))
    g1_out = []
    g2_out = []
    for letter in active_alphabet:
        g1_out += [0] * g1_subcol.count(letter) + [1]
        g2_out += [0] * g2_subcol.count(letter) + [1]

    return g1_out, g2_out, len(active_alphabet)

def check(col, g1s, g1e, g2s, g2e):
    included = set()
    for i in range(g1s, g1e):
        included.add(g1.edge_label(i)[-col:-1])
    for i in range(g2s, g2e):        
        included.add(g2.edge_label(i)[-col:-1])
        
    if not (len(included) == 1):
        print("included", len(included), "col", col, included)
        print("g1[", g1s, g1e,"]")
        print("g2[", g2s, g2e,"]")
        for j in range(g1s, g1e):
            print(j,g1.edge_label(j))
        print("---")
        for j in range(g2s, g2e):
            print(j, g2.edge_label(j))

def refine_sets(cols, sets, colno):
    g1_col, g2_col = cols
    g1_sets, g2_sets = sets
    g1_out_set = []
    g2_out_set = []
    g1_ptr = 0
    g2_ptr = 0

    assert g1_sets ==  [item for sublist in set_iter(g1_sets) for item in sublist]
    assert g2_sets ==  [item for sublist in set_iter(g2_sets) for item in sublist]
    assert g1_sets.count(1) == len(list(set_iter(g1_sets)))
    assert g2_sets.count(1) == len(list(set_iter(g2_sets)))    

    L = []
    for  (g1_set, g2_set) in zip(set_iter(g1_sets), set_iter(g2_sets)):
        assert(g1_set[-1] == 1)
        assert(g1_set.count(1) == 1)
        assert(g2_set[-1] == 1)
        assert(g2_set.count(1) == 1)
        
        g1_num = len(g1_set) - 1
        g2_num = len(g2_set) - 1
        if g2_ptr <= 181 <= g2_ptr+g2_num and col == 2:
            debug=True
            r = g2_col[g2_ptr:g2_ptr+g2_num]
            print("problem range:", g2_ptr, g2_ptr+g2_num, r)
        else:
            debug=False
        check(col, g1_ptr, g1_ptr + g1_num, g2_ptr, g2_ptr + g2_num)
        g1_subsets, g2_subsets, active_alpha_size = subdivide(g1_col[g1_ptr:g1_ptr + g1_num],
                                           g2_col[g2_ptr:g2_ptr + g2_num])
        if colno == 0:
            L += [0] * (active_alpha_size - 1) + [1]
        if debug:
            print("subsets", g2_subsets)
            st = 0
            for s in set_iter(g2_subsets):
                n = len(s) - 1
                print(r[st:st+n])
                st += n
        g1_out_set += g1_subsets
        g2_out_set += g2_subsets
        g1_ptr += g1_num
        g2_ptr += g2_num

    if len(L) > 0:
        print("s/b num ones", len(list(set_iter(g1_sets))))
        lfile = open("L", "w")
        lfile.write("\n".join(map(str,L)))
        lfile.close()

    return g1_out_set, g2_out_set
        
    
            
# main merge

# initialize sets to put all elements in the same equivalence class
# sets are contiguous runs of 0's which each indicate that for each rank_0 element,
# the corresponding element of BWT appears to be included in that set (so far)
g1_sets = [0] * g1.num_edges + [1]
g2_sets = [0] * g2.num_edges + [1]

col=2
f=open("preg2c" + str(col), "w")
g2_col = get_column(g2, col)
for c in g2_col: f.write(c+"\n")


for colno, col in enumerate([i + 1 for i in range(g1.k)] + [0]):
    print ("doing column", col, "g1 count:", g1_sets.count(1), "g2 count:", g2_sets.count(1))
    print (g1_sets.count(1) - len(g1_sets))
    print (g2_sets.count(1) - len(g2_sets))
    g1_col = get_column(g1, col)
    f=open("g2c" + str(col), "w")
    g2_col = get_column(g2, col)
    for c in g2_col: f.write(c+"\n")
    f.close()
    g1_sets, g2_sets = refine_sets((g1_col, g2_col), (g1_sets, g2_sets), col)

# initsets = (g1_sets, g2_sets) # (([0] * g1.num_edges + [1]), ([0] * g2.num_edges + [1]))
# colgen = ((get_column(g1, col), get_column(g2, col)) for  col in [i + 1 for i in range(g1.k)] + [0])
# g1_sets, g2_sets = reduce(refine_sets, colgen, initsets)
    
g1_ptr = 0
g2_ptr = 0
print ("k=", g1.k)
print (g1_sets.count(1),"/",len(g1_sets),",",g2_sets.count(1),"/", len(g2_sets))
for g1_set, g2_set in zip(set_iter(g1_sets), set_iter(g2_sets)):
    if g1_set[0] == 0:
        print (g1.edge_label(g1_ptr)) #g1._edges[g1_ptr]
        g1_ptr += 1
        if g2_set[0] == 0:
            g2_ptr += 1
    else:
        print (g2.edge_label(g2_ptr)) #g2._edges[g2_ptr]
        g2_ptr += 1
