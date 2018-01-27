import itertools as it
from utility import *
from bisect import bisect_left, bisect_right

def rank(symbol, sequence, i):
  return sequence[:i+1].count(symbol)

def oldselect(symbol, sequence, i):
  if i <= 0: return -1
  ranks = (rank(symbol, sequence, i) for i in range(len(sequence)))
  return next(it.dropwhile(lambda __x: __x[1]<i, enumerate(ranks)), (None,None))[0]

# this method is slower, 10 seconds vs 4 seconds for soln below
# https://stackoverflow.com/questions/8337069/find-the-index-of-the-nth-item-in-a-list
from itertools import compress, count,  islice
from functools import partial
from operator import eq

memo = {}
def qselect(item, iterable, i):
  if id(iterable) not in memo: memo[id(iterable)] = compress(count(), map(partial(eq, item), iterable))
  if i <= 0: return -1
  n = i - 1
#  indicies = memo[id(iterable)] #
  indicies = compress(count(), map(partial(eq, item), iterable))
  return next(islice(indicies, n, None), -1)
      
def select(symbol, sequence, i):
  if i <= 0:
#    print "select => -1"
    return -1
  s = oldselect(symbol, sequence, i)
#  if not s or  s < 0: print "select => -1"
  return s
#  print("oldselect(", symbol, i, ") => ", oldselect(symbol, sequence, i))
  start = 0
  for j in range(i):
    try:
      found = sequence.index(symbol, start)
    except ValueError:
      return -1
    start = found + 1
  assert found == oldselect(symbol, sequence, i)
#  print("select(", symbol, i,") => ", found)
  return found


class debruijn_graph:
  def __init__(self, k, F, last, edges, edge_flags):
    alphabet = sorted(list(set(edges)))
    self._F = dict(list(zip(alphabet, F)))
    self._F_inv = lambda i: alphabet[bisect_left(F, i, 0, bisect_right(F, i) - 1)]
    self._last = last
    self._edges = [c + ("","-")[x] for c,x in zip(edges,edge_flags)]
    self.num_edges = len(edges)
    self.num_nodes = sum(last)
    self.k = k

  def _fwd(self, i):
    c = self._edges[i][0] # [0] to remove minus flag
    if c == "$": return -1
    base_c = self._F[c]
    rank_c = rank(c, self._edges, i) # how many Cs away from base, but only if they are marked as last
    prev_1s = rank(1, self._last, base_c - 1)
    return select(1, self._last, prev_1s + rank_c)

  def _bwd(self, i):
    c = self._F_inv(i)
    if c == "$": return -1
    base_c = self._F[c] # find the base first, then find how many cs, then select to it
    pre_base_rank = rank(1, self._last, base_c - 1)
    prev_rank = rank(1, self._last, i - 1)
    n = prev_rank - pre_base_rank + 1 # nth edge with label c
    return select(c, self._edges, n)

  def _first_edge(self, v):
    return select(1, self._last, v) + 1

  def _last_edge(self, v):
    return select(1, self._last, v + 1)

  def _node_range(self, v):
    return (self._first_edge(v), self._last_edge(v))

  def _edge_to_node(self, i):
    if i == 0: return 0
    return rank(1, self._last, i - 1)

  def outdegree(self, v):
    first, last = self._node_range(v)
    return last - first + 1

  def outgoing(self, v, c):
    if c == "$": return -1
    first, last = self._node_range(v)
    for x in (c, c + "-"):
      prev_cs = rank(x, self._edges, last)
      last_c_pos = select(x, self._edges, prev_cs)
      if first <= last_c_pos <= last:
        return rank(1, self._last, self._fwd(last_c_pos)) - 1
    return -1

  def successors(self, v):
    first, last = self._node_range(v)
    for x in range(first, last + 1):
      yield rank(1, self._last, self._fwd(x)) - 1

  def indegree(self, v):
    i = self._last_edge(v)
    first_pred = self._bwd(i)
    if first_pred == -1: return 0
    c = self._edges[first_pred]
    next_node = select(c, self._edges, first_pred + 1) or self.num_edges - 1
    return rank(c+"-", self._edges, next_node) - rank(c+"-", self._edges, first_pred) + 1

  def incoming(self, v, c):
    i = self._last_edge(v)
    first_pred = self._bwd(i)
    if first_pred == -1: return -1
    e = self._edges[first_pred]
    next_node = select(e, self._edges, first_pred + 1) or self.num_edges - 1
    flags_before_base = rank(e+"-", self._edges, first_pred)
    indegree = rank(e+"-", self._edges, next_node) - flags_before_base + 1
    get_first_char = lambda i: nth(self.k - 1, self._label_iter(i))
    selector = lambda i: select(e+"-", self._edges, flags_before_base + i) if i > 0 else first_pred
    accessor = lambda i: get_first_char(selector(i))
    a = array_adaptor(accessor, indegree)
    sub_idx = get_index(a, c)
    if sub_idx == -1: return -1
    return self._edge_to_node(selector(sub_idx))

  def _label_iter(self, i):
#    print("_label_iter(", i, ") called")
    while True:
#      print("yielding self._F_inv(i), where i=", i)
      __y = self._F_inv(i)
#      print("  =>", __y)
      yield __y
#      print("calling self._bwd(",i,")")
      i = self._bwd(i)
#      print("  =>", i)

  def label(self, v):
    i = self._first_edge(v)
    return "".join(take(self.k, self._label_iter(i))[::-1])

  def edge_label(self, i):
    return "".join(take(self.k, self._label_iter(i))[::-1]) + self._edges[i][0]

  def get_column(self, col_num):
    column = []
    for i in range(self.num_edges):
        if col_num == 0:
            column.append(self._edges[i][0])
        else:
            for j in range(col_num - 1):
                i = self._bwd(i)
            column.append(self._F_inv(i))
    return column

  @staticmethod
  def load(filename):
    with open(filename, "r") as f:
      lines = f.readlines()
    edges = [(int(l),e,int(f)) for l,e,f in (x.strip().split() for x in lines[:-2])]
    last, edges, flags = list(map(list, list(zip(*edges))))
    F = list(map(int, lines[-2].split()))
    k = int(lines[-1])
    return debruijn_graph(k, F, last, edges, flags)
