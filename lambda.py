import sys, functools

from ast import Node



c0 = (
  Node('Func')
    .addkid(Node('NAME').addkid('s'))
    .addkid(Node('Expr')
      .addkid(Node('Func')
        .addkid(Node('NAME').addkid('z'))
        .addkid(Node('Expr')
          .addkid(Node('NAME').addkid('z'))
        )
      )
    )
  )

succ = (
  Node('Func')
    .addkid(Node('NAME').addkid('n'))
    .addkid(Node('Expr')
      .addkid(Node('Func')
        .addkid(Node('NAME').addkid('s'))
        .addkid(Node('Expr')
          .addkid(Node('Func')
            .addkid(Node('NAME').addkid('z'))
            .addkid(Node('Expr')
              .addkid(Node('Apply')
                .addkid(Node('NAME').addkid('s'))
                .addkid(Node('Expr')
                  .addkid(Node('Apply')
                    .addkid(Node('Apply')
                      .addkid(Node('NAME').addkid('n'))
                      .addkid(Node('Expr').addkid(Node('NAME').addkid('s')))
                    )
                    .addkid(Node('Expr').addkid(Node('NAME').addkid('z')))
                  )
                )  
              )
            )
          )
        )
      )
    )
  )

expr = Node('Expr').addkid(Node('Apply').addkid(succ).addkid(c0))

def replace(node, name, expr):
  if   node.label == 'NAME' and reduce(node) == name:
    return expr
  elif node.label == 'NAME':
    return node
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
    #print 'Func :', name.label, expr.label
    if not isinstance(reduce(expr), Node):
      expr = expr
    else:
      expr = reduce(expr)
    return Node('Func').addkid(name).addkid(expr)
  def Apply(fun, expr):
    #print 'Apply :', fun.label, fun.children, expr.label
    if fun.label == 'NAME': 
      return Node('Apply').addkid(fun).addkid(expr)
    #print 'ehlo'
    name = reduce(fun.children[0])
    body = fun.children[1]
    #print body
    #print 'replacing', repr(name), expr.label
    body_ = replace(body, name, expr)
    #print 'replaced name %s with expr' % name
    #print
    body = reduce(body_)
    #print fun.label, fun.children
    #print 'Apply :', name
    #print body_ 
    #print '-----'
    #print body
    #print
    return body
  def NAME(name):
    return name
  def NUMBER(number):
    return number
  cmds.update({name:obj for name,obj in locals().iteritems() if type(obj) == type(reduce)})

  return cmds[node.label](*node.children)

print reduce(expr).dotty()



