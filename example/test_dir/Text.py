'''
>>> print(__name__)
text_dir.Texts
'''

def test_func():
  '''
  >>> test_func()
  for test
  '''
  print('for test')

class Test:
  '''
  >>> Test().output('cator vee')
  cator vee

  >>> print(Test().addition(2, 5)))
  7

  >>> print(Test().subtraction(5, 2), Test().subtraction(5, 2), 'subtraction')
  3 3 subtraction
  '''
  def output(self, msg):
    print(msg)

  def addition(self, x, y):
    return x + y

  def subtraction(self, x, y):
    return x - y

  def do_nothing(self):
    print('nothing')