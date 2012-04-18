
import os, random, timeit

import editdist, numpy

random.seed()
DEBUG = False
_cache = dict()

def distance(a,b):
  if (a,b) in _cache: return _cache[(a,b)]
  _cache[(b,a)] = _cache[(a,b)] = d = float(editdist.distance(a,b))
  return d
d = distance

def select_pivot(objs):
  S = random.sample(objs, min(10, len(objs)))
  if len(S) == 0: S = objs
  maxvar = (0, None)
  if DEBUG:
    print S
  for a in S:
    dists = list()
    for b in S:
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

def search(q, S, t=None):
  pivot = select_pivot(S)
  radius = select_radius(pivot, S)
  inn, out = split(pivot, radius, S)
  d = distance(q, pivot)
  if t == None: t = d
  if d > t: t = d
  best = list()
  if d <= t: 
    best.append((pivot, d))
  if inn and d - t <= radius:
    res = search(q, inn, t)
    if res is not None: best.append(res)
  if out and d + t >= radius:
    res = search(q, out, t)
    if res is not None: best.append(res)
  if not best: return None
  return min(((x, dx) for x, dx in best), key=lambda x:x[1]) 

def brute_search(q, S):
  return min(
    ((a, d(a,q)) 
      for a in S),
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

S = list(set(chunks(text, 30)))[:500]
q = random.choice(S)
S.remove(q)

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

print q, timeit.timeit(lambda:brute_search(q,S), number=1)
print q, timeit.timeit(lambda:search(q,S), number=1)

