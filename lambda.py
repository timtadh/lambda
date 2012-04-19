import sys, functools

from ast import Node



c0 = (
  Node('Func')
    .addkid(Node('NAME').addkid('s'))
    .addkid(Node('Func')
      .addkid(Node('NAME').addkid('z'))
      .addkid(Node('NAME').addkid('z'))
    )
  )  

succ = (
  Node('Func')
    .addkid(Node('NAME').addkid('n'))
    .addkid(Node('Func')
      .addkid(Node('NAME').addkid('s'))
      .addkid(Node('Func')
        .addkid(Node('NAME').addkid('z'))
        .addkid(Node('Apply')
          .addkid(Node('NAME').addkid('s'))
          .addkid(Node('Apply')
            .addkid(Node('Apply')
              .addkid(Node('NAME').addkid('n'))
              .addkid(Node('NAME').addkid('s'))
            )
            .addkid(Node('NAME').addkid('z'))
          )
        )  
      )
    )
  )


plus = (
  Node('Func')
    .addkid(Node('NAME').addkid('m'))
    .addkid(Node('Func')
      .addkid(Node('NAME').addkid('n'))
      .addkid(Node('Func')
        .addkid(Node('NAME').addkid('s'))
        .addkid(Node('Func')
          .addkid(Node('NAME').addkid('z'))
          .addkid(Node('Apply')
            .addkid(Node('Apply')
              .addkid(Node('NAME').addkid('m'))
              .addkid(Node('NAME').addkid('s'))
            )
            .addkid(Node('Apply')
              .addkid(Node('Apply')
                .addkid(Node('NAME').addkid('n'))
                .addkid(Node('NAME').addkid('s'))
              )
              .addkid(Node('NAME').addkid('z'))
            )
          ) 
        )
      )
    )
  )

c1 = Node('Apply').addkid(succ).addkid(c0)
c2 = Node('Apply').addkid(succ).addkid(c1)
c3 = Node('Apply').addkid(succ).addkid(c2)
c4 = Node('Apply').addkid(succ).addkid(c3)
c7 = Node('Apply').addkid(Node('Apply').addkid(plus).addkid(c4)).addkid(c3)


def getconst(node):
  return node.children[0]

def replace(node, name, expr):
  print 'replace', node.label, name, expr.label
  if   node.label == 'NAME' and getconst(node) == name:
    return expr
  elif node.label == 'NAME':
    return node
  elif node.label == 'Func':
    if getconst(node.children[0]) == name:
      return node
    else:
      return (Node('Func')
          .addkid(node.children[0])
          .addkid(replace(node.children[1], name, expr)))
  elif node.label == 'Apply':
    if node.children[0].label == 'NAME' and getconst(node.children[0]) == name:
      if expr.label not in ('NAME', 'Func', 'Apply'):
        raise Exception, expr.label
  return Node(
      node.label, 
      children=[replace(x, name, expr) for x in node.children])

def reduce(node, map=None):
  if map is None: map = dict()
  cmds = dict()
  def Expr(typ):
    #print 'Expr :', typ.label
    return reduce(typ)
  def Func(name, expr):
    print 'Func :', getconst(name), expr.children
    return Node('Func').addkid(name).addkid(reduce(expr))
  def Apply(fun, expr):
    print 'Apply :', fun.label, fun.children, expr.label, expr.children
    if fun.label == 'NAME': 
      return Node('Apply').addkid(fun).addkid(reduce(expr))
    elif fun.label == 'Func':
      #print 'ehlo'
      name = getconst(fun.children[0])
      body = fun.children[1]
      body_ = replace(body, name, reduce(expr))
      body__ = reduce(body_)
      #print fun.label, fun.children
      #print 'Apply :', name
      #print body
      #print '-----'
      #print expr
      #print '-----'
      #print body_
      #print '-----'
      #print body__
      #print
      return body__
    elif fun.label == 'Apply':
      print 'here'
      fun = reduce(fun)
      if fun.label in ('NAME', 'Func'):
        return Apply(fun, reduce(expr))
      elif fun.label == 'Apply':
        return Node('Apply').addkid(fun).addkid(reduce(expr))
      else:
        raise Exception, fun.label
    else:
      print '\n'*3
      print fun
      raise Exception, fun.label
  def NAME(name):
    return Node('NAME').addkid(name)
  def NUMBER(number):
    return Node('NUMBER').addkid(number)
  cmds.update({name:obj for name,obj in locals().iteritems() if type(obj) == type(reduce)})
  print 'reducing', node.label, node.children
  return cmds[node.label](*node.children)

expr = Node('Expr').addkid(Node('Apply').addkid(succ).addkid(c4))
print >>sys.stderr, reduce(c7).dotty()



