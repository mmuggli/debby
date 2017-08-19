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

def refine_sets(cols, sets, colno):
    g1_col, g2_col = cols
    g1_sets, g2_sets = sets
    g1_out_set = []
    g2_out_set = []
    g1_ptr = 0
    g2_ptr = 0

    L = []
    for  (g1_set, g2_set) in zip(set_iter(g1_sets), set_iter(g2_sets)):
        
        g1_num = len(g1_set) - 1
        g2_num = len(g2_set) - 1
        g1_subsets, g2_subsets, active_alpha_size = subdivide(g1_col[g1_ptr:g1_ptr + g1_num],
                                                              g2_col[g2_ptr:g2_ptr + g2_num])
        if colno == 0:
            L += [0] * (active_alpha_size - 1) + [1]

        g1_out_set += g1_subsets
        g2_out_set += g2_subsets
        g1_ptr += g1_num
        g2_ptr += g2_num

    return g1_out_set, g2_out_set, L
        
    
            
# main merge

# initialize sets to put all elements in the same equivalence class
# sets are contiguous runs of 0's which each indicate that for each rank_0 element,
# the corresponding element of BWT appears to be included in that set (so far)
g1_sets = [0] * g1.num_edges + [1]
g2_sets = [0] * g2.num_edges + [1]

def flagdump(flags):
    icount = 0
    for i in flags:
        if i == 0:
            icount += 1
            print (i, icount)
        else:
            print(i)
            

L = []
for colno, col in enumerate([i + 1 for i in range(g1.k)] + [0]):
    g1_col = get_column(g1, col)
    g2_col = get_column(g2, col)
    g1_sets, g2_sets, Lval = refine_sets((g1_col, g2_col), (g1_sets, g2_sets), col)
    L += Lval
    if col == g1.k - 1:
        g1_flagsets, g2_flagsets = g1_sets, g2_sets
        #flagdump(g1_flagsets)
        

    
g1_ptr = 0 # keeps track of consumed symbols in g1._edges
g2_ptr = 0 # keeps track of consumed symbols in g1._edges
g1f_ptr = 0
g2f_ptr = 0


class Flags():
    def __init__(self, g1_flagsets, g2_flagsets):
        self.g1_flagsets, self.g2_flagsets = g1_flagsets, g2_flagsets
        self.flagsets_iter = zip(set_iter(self.g1_flagsets), set_iter(self.g2_flagsets))
        self.cur_flagsets = self.flagsets_iter.__next__()
        self.newflags =  set()
        self.g1_ptr, self.g2_ptr = 0,0

        
    def seen(self, nt): return nt in self.newflags

    def add(self, nt): self.newflags.add(nt)

    def __check_flagsets(self):
        # if all the flagsets now point to their end marker, then move on to the next flagsets
        if self.cur_flagsets[0][self.g1_ptr] == 1 and self.cur_flagsets[1][self.g2_ptr] == 1:
            try:
                self.cur_flagsets = self.flagsets_iter.__next__()
            except StopIteration as e:
                pass
            self.g1_ptr, self.g2_ptr = 0,0
            self.newflags = set()

    
    def adv_g1(self):
        self.g1_ptr += 1
        self.__check_flagsets()

    def adv_g2(self):
        self.g2_ptr += 1
        self.__check_flagsets()        
    
flags = Flags(g1_flagsets, g2_flagsets)
ntcounts = {'A':0, 'C':0, 'G':0,'T':0}

for out_ptr, (g1_set, g2_set) in enumerate(zip(set_iter(g1_sets), set_iter(g2_sets))):
    if g1_set[0] == 0:
        print (L[out_ptr], g1._edges[g1_ptr][0], end=" ")
        ntcounts[g1.edge_label(g1_ptr)[g1.k-1]] += 1

        if flags.seen(g1._edges[g1_ptr][0]):
#            print (g1.edge_label(g1_ptr), end=" ")
            print (1)
        else:
#            print (g1.edge_label(g1_ptr), end=" ")
            print (0)
        flags.add(g1._edges[g1_ptr][0])

        g1_ptr += 1
        flags.adv_g1()
        
        if g2_set[0] == 0:
            g2_ptr += 1
            flags.adv_g2()

    else:
        assert g2_set[0] == 0
        print (L[out_ptr], g2._edges[g2_ptr][0], end=" ")
        ntcounts[g2.edge_label(g2_ptr)[g1.k-1]] += 1                 

        if flags.seen(g2._edges[g2_ptr][0]):

#            print (g2.edge_label(g2_ptr), end=" ")
            print (1)
        else:
#            print (g2.edge_label(g2_ptr), end=" ")
            print (0)
        flags.add(g2._edges[g2_ptr][0])

        g2_ptr += 1
        flags.adv_g2()
print(0, ntcounts['A'], ntcounts['A'] + ntcounts['C']  , ntcounts['A'] + ntcounts['C'] + ntcounts['G'] )
print(g1.k)
