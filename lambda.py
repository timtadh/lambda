#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, functools

from ast import Node

def f(_, e): 
  return Node('Func').addkid(n(_)).addkid(e)
def a(a, b):
  return Node('Apply').addkid(a).addkid(b)
def n(_): 
  return Node('NAME').addkid(_)
def N(_):
  return Node('NUMBER').addkid(_)

builtins = {
  '+':(lambda a:(lambda b:N(getconst(a)+getconst(b)))),
  '-':(lambda a:(lambda b:N(getconst(a)-getconst(b)))), 
  '*':(lambda a:(lambda b:N(getconst(a)*getconst(b)))), 
  '/':(lambda a:(lambda b:N(getconst(a)/getconst(b)))),
 '==':(lambda a:(lambda b:(true if getconst(a)==getconst(b) else false))),
}

def church(node):
  assert node.label == 'NUMBER'
  num = getconst(node)
  node = n('z')
  while num:
    node = a(n('s'),node)
    num -= 1
  return f('s', f('z', node))

def natural(node):
  assert node.label == 'Func'
  assert getconst(node.children[0]) == 's'
  node = node.children[1]
  assert node.label == 'Func'
  assert getconst(node.children[0]) == 'z'
  node = node.children[1]
  def natural(node):
    if node.label == 'Apply':
      assert getconst(node.children[0]) == 's'
      return 1 + natural(node.children[1])
    elif node.label == 'NAME':
      assert getconst(node) == 'z'
      return 0
    else:
      raise Exception, repr(node)
  return N(natural(node))

builtins.update({'NN':natural, 'C':church})

succ = f('n', f('s', f('z', 
        a(n('s'),            a(a(n('n'), n('s')), n('z'))))))
plus = f('m', f('n', f('s', f('z', 
        a(a(n('m'), n('s')), a(a(n('n'), n('s')), n('z')))))))
c0 = f('s', f('z', n('z')))
c1 = a(succ, c0)
c2 = a(succ, c1)
c3 = a(succ, c2)
c4 = a(succ, c3)
c5 = a(succ, c4)
c6 = a(succ, c5)
c9 = a(a(plus, c4), c5)
c18 = a(a(plus, c9), c9)

#true ≡ λa.λb. a
true = f('a', f('b', n('a')))
#false ≡ λa.λb. b 
false = f('a', f('b', n('b')))
#if ≡ λm.λa.λb. m a b
If = f('m', f('a', f('b', a(a(n('m'), n('a')), n('b')))))
#and ≡ λm.λn. m n m
And = f('m', f('n', a(a(n('m'), n('n')), n('m'))))
#or ≡ λm.λn. m m n
Or = f('m', f('n', a(a(n('m'), n('m')), n('n'))))
#not ≡ λm.λa.λb. m b a
Not = f('x', a(a(a(If, n('x')), false), true))
#zero? ≡ λn. n (λx.F) T 
zero = f('n', a(a(n('n'), f('x', false)), true))
#equal?
equals = f('n', f('m', a(a(n('=='), a(n('NN'), n('n'))), a(n('NN'), n('m')))))
#equals = f('m', a(n('=='), a(n('NN'), n('m'))))


def getconst(node):
  assert node.label in ('NAME', 'NUMBER')
  return node.children[0]

def replace(node, name, expr):
  if not hasattr(node, 'label'):
    return node
  elif node.label == 'NAME' and getconst(node) == name:
    return expr
  elif node.label == 'NAME':
    return node
  elif node.label == 'Func':
    if getconst(node.children[0]) == name:
      return node
    else:
      return f(getconst(node.children[0]), replace(node.children[1], name, expr))
  return Node(
      node.label, 
      children=[replace(x, name, expr) for x in node.children])

def reduce(node, map=None):
  if map is None: map = dict()
  cmds = dict()
  def Expr(typ):
    return reduce(typ)
  def Func(name, expr):
    return Node('Func').addkid(name).addkid(reduce(expr))
  def Apply(fun, expr):
    if hasattr(fun, '__call__'):
      expr = reduce(expr)
      if hasattr(expr, 'label') and expr.label in ('NAME', 'Apply'):
        return a(fun, expr)
      return fun(expr)
    elif fun.label == 'NAME': 
      name = getconst(fun)
      if name in builtins:
        fun = builtins[name]
        return Apply(fun, expr)
      return Node('Apply').addkid(fun).addkid(reduce(expr))
    elif fun.label == 'Func':
      name = getconst(fun.children[0])
      body = fun.children[1]
      return reduce(replace(body, name, reduce(expr)))
    elif fun.label == 'Apply':
      fun = reduce(fun)
      if hasattr(fun, 'label') and fun.label == 'Apply':
        return a(fun, reduce(expr))
      else:
        return Apply(fun, reduce(expr))
    else:
      print '\n'*3
      print fun
      raise Exception, fun.label
  def NAME(name):
    return Node('NAME').addkid(name)
  def NUMBER(number):
    return Node('NUMBER').addkid(number)
  cmds.update({name:obj for name,obj in locals().iteritems() if type(obj) == type(reduce)})
  return cmds[node.label](*node.children)


#print >>sys.stderr, reduce(c9).dotty()
#res = reduce(a(n('C'), a(a(n('*'),a(n('NN'),c2)), a(n('NN'),c3))))
#res = reduce(a(a(n('+'), N(3)),N(5)))
expr = a(n('NN'), a(a(a(If, a(a(equals,church(N(200))),church(N(201)))), c1), c0))
#expr = a(n('NN'), a(a(a(If, a(a(n('=='),N(2)),N(1))), c1), c0))
#expr = a(a(equals,c0),c0)
res = reduce(expr)
print res
print >>sys.stderr, res.dotty()

