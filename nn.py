
import os, random, timeit, functools, collections

import editdist, numpy

random.seed()
DEBUG = False
_cache = dict()

count = [0]
def distance(a,b):
  count[0] += 1
  if (a,b) in _cache: return _cache[(a,b)]
  d = float(editdist.distance(a,b))
  #d = d/(1+d)
  _cache[(b,a)] = _cache[(a,b)] = d
  return d
d = distance

def select_pivot(objs):
  S = random.sample(objs, min(10, len(objs)))
  if len(S) == 0: S = objs
  maxvar = (0, None)
  if DEBUG:
    print S
  for i, a in enumerate(S):
    dists = list()
    for b in S[i:]:
      d = distance(a,b)
      if DEBUG:
        sys.stdout.write('.')
        sys.stdout.flush()
      dists.append(d)
    variance = numpy.var(dists)
    if variance >= maxvar[0]:
      maxvar = (variance, a)
    if DEBUG:
      print maxvar, variance
  return maxvar[1]

def select_radius(pivot, objs):
  dists = list()
  for b in objs:
    d = distance(pivot,b)
    if DEBUG:
      sys.stdout.write('.')
      sys.stdout.flush()
    dists.append(d)
  return numpy.median(dists)

def split(pivot, radius, objs):
  inn = list()
  out = list()
  for b in objs:
    if b == pivot: continue
    d = distance(pivot, b)
    if d < radius: inn.append(b)
    else: out.append(b)
  return inn, out

def group(pivot, objs):
  groups = dict()
  for b in objs:
    if b == pivot: continue
    d = distance(pivot, b)
    group = groups.get(d, list())
    group.append(b)
    groups[d] = group
  return groups

def search(q, S):
  dists = [distance(q,x) for x in random.sample(S, min(max(25, int(len(S)*.001)), len(S)))]
  t = min(dists)
      #[distance(q,x) 
      #for x in random.sample(S, min(max(25, int(len(S)*.01)), len(S)))])
  print 't ->', t,
  stack = list()
  stack.append(S)
  best = (None, 100000000)
  count = 0
  while stack:
    count += 1
    S = stack.pop()
    pivot = random.choice(S)
    groups = group(pivot, S)
    d = distance(q, pivot)
    if t == None: t = d
    if d < t: t = d
    best = min((best, (pivot, d)), key=lambda x:x[1])
    for dx, g in groups.iteritems():
      if d - t < dx and dx < d + t:
        stack.append(g)
  print 'count', count,
  return best

def build_tree(S):
  root = None
  stack = collections.deque()
  stack.append((S, lambda objs: None))
  while stack:
    objs, continue_f = stack.pop()
    if not objs:
        continue_f(None)
        continue
    pivot = select_pivot(objs)
    groups = group(pivot, objs)
    p = vpnode(pivot)
    for dx,g in groups.iteritems():
      stack.append((g, functools.partial(p.add, dx)))
    continue_f(p)
    if root is None: root = p
  return root

class vpnode(object):

  __slots__ = ['pivot', 'groups']

  def __init__(self, pivot):
    self.pivot = pivot
    self.groups = dict()

  def add(self, dx, node):
    self.groups[dx] = node

  def search(self, q, S):
    #S_ = random.sample(S, min(max(50, int(len(S)*.01)), len(S)))
    #dists = [distance(q,b) for b in S_]
    #t = min(dists)
    t = None
    stack = list()
    stack.append(self)
    best = (None, 100000000)
    count = 0
    while stack:
      count += 1
      node = stack.pop()
      d = distance(q, node.pivot)
      if t == None: t = d
      if d < t: t = d
      if q != node.pivot:
        best = min((best, (node.pivot, d)), key=lambda x:x[1])
      for dx, g in node.groups.iteritems():
        if (d - dx)**2 <= best[1]**2:
          stack.append(g)
    return best

def brute_search(q, S):
  return min(
    ((a, distance(a,q)) 
      for a in S if a != q),
    key=(lambda x: x[1])
  )

with open('sample.txt', 'r') as f: 
  text = (f.read().replace('\n', '').replace('\r', '').
                    replace('\t', '').replace(' ', '').
                    replace('"', '').replace("'", '').
                    replace('.', '').replace(',', '').
                    replace('!', '').replace('?', '').
                    replace('(', '').replace(')', '').
                    lower()
  )

def chunks(l, n):
  'Yield successive n-sized chunks from l. '
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

S = list(set(chunks(text, 50)))[:500]
#S = [os.urandom(10) for x in xrange(10000)]


#print min(
#    # 0  1  2  3       4       5       6
#    ((q, a, b, d(a,q), d(b,q), d(a,b), d(a,q)+d(b,q)) 
#      for i, a in enumerate(S) for b in S[i+1:]),
#    key=(lambda x: x[6]-x[5])
#)

#print min(
#    # 0  1  2  3       4       5       6
#    ((q, a, b, d(a,q), d(b,q), d(a,b), d(a,q)+d(b,q)) 
#      for i, a in enumerate(S) for b in S[i+1:]),
#    key=(lambda x: x[5])
#)



#pivot = select_pivot(S)
#S.remove(pivot)
#radius = select_radius(pivot, S)
#inn, out = split(pivot, radius, S)
#print 'pivot', pivot
#print 'radius', radius
#print 'split', len(inn), len(out)
#print 'avg inn', numpy.mean([d(pivot,x) for x in inn])
#print 'avg out', numpy.mean([d(pivot,x) for x in out])

#print brute_search(q,S)
#print search(q,S,t)
#print count, len(S)
#print p, brute_search(p,S)
#print p, root.search(p,S)
#print q, brute_search(q,S)
#print q, root.search(q,S)
p = random.choice(S)
q = random.choice(S)
root = build_tree(S)
def compute_brute():
  for x in xrange(10):
    _cache.clear()
    np,dn = brute_search(p,S)
    print p[:10], np[:10], dn
    brute_search(q,S)

def compute_vptree():
  for x in xrange(10):
    _cache.clear()
    np,dn = root.search(p,S)
    print p[:10], np[:10], dn
    root.search(q,S)

count = [0]
print timeit.timeit(compute_brute, number=1)
print count, len(S)
count = [0]
print timeit.timeit(compute_vptree, number=1)
print count, len(S)

