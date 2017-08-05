import itertools as it
def rank(symbol, sequence, i):
  return sequence[:i+1].count(symbol)

# def select(symbol, sequence, i):
#   if i <= 0: return -1
#   ranks = (rank(symbol, sequence, i) for i in range(len(sequence)))
#   return next(it.dropwhile(lambda __x: __x[1]<i, enumerate(ranks)), (None,None))[0]

def select(symbol, sequence, i):
  if i <= 0: return -1
  start = 0
  for j in range(i):
      found = sequence.index(symbol, start)
      start = found + 1
  return found



t = [1,0,1,1,0,0,1,0,1,0,0,0,1,0,1]

for i in range(t.count(1)):
    print(select(1,t,i+1))
