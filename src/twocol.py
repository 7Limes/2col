import sys
import os
import time

COMMANDS = {
  '!': 'print',
  '#': 'addstack',
  '&': 'popstack',
  '+': 'add',
  '-': 'sub',
  '*': 'mul',
  '/': 'div',
  '%': 'mod',
  '?': 'if',
  '^': 'jump',
  '$': 'swap'
}

class twocolError(Exception):
  pass

class TwocolInterpreter:
  def __init__(self, debug=True):
    self.debug = debug
  
  def interpret(self, script):
    startTime = time.perf_counter()
    self.lines = open(script).read().split('\n')
    self.lines = [l.strip().replace(' ','') for l in self.lines]
    self.lines = [l for l in self.lines if l != '']
    self.lineNum = 0
    self.stack = []
    self.labels = {}

    # initialize labels
    for i, line in enumerate(self.lines):
      if line[0] == '@':
        self._add_label(line[1:], i)

    while self.lineNum < len(self.lines):
      line = self.lines[self.lineNum]
      cmd = line[0]
      value = line[1:]
      if line[0] != '~' and cmd in COMMANDS:
        try:
          getattr(self, f'_cmd_{COMMANDS[cmd]}', None)(value)
        except IndexError:
          self._error('tried to reference nonexistent stack value')
      
      self.lineNum += 1

    if self.debug:
      self._print_debug_info(startTime)

  def _print_debug_info(self, st):
    print()
    print(self.stack)
    print(self.labels)
    print(f'interpreted in {time.perf_counter()-st:.4f} s')
  
  def _format_value(self, value):
    if value[0] == '.':
      return chr(self._format_value(value[1:]))
    if value == 'p':
      return self.stack.pop(0)
    if value == 'c':
      return self.stack[0]
    if value == 'i':
      return int(input('> '))
    return int(value)
  
  def _cmd_print(self, value):
    print(self._format_value(value), end='')
  
  def _cmd_addstack(self, value):
    if '.' not in value:
      self.stack.insert(0, self._format_value(value))
  
  def _cmd_popstack(self, value):
    self.stack.pop(0)
  
  def _cmd_add(self, value):
    self.stack.insert(0, self.stack.pop(1)+self.stack.pop(0))
  
  def _cmd_sub(self, value):
    self.stack.insert(0, self.stack.pop(1)-self.stack.pop(0))
  
  def _cmd_mul(self, value):
    self.stack.insert(0, self.stack.pop(1)*self.stack.pop(0))
  
  def _cmd_div(self, value):
    self.stack.insert(0, self.stack.pop(1) // self.stack.pop(0))
  
  def _cmd_mod(self, value):
    self.stack.insert(0, self.stack.pop(1) % self.stack.pop(0))
  
  def _cmd_if(self, value):
    if value:
      if '.' not in value and self.stack[0] == self._format_value(value):
        self.lineNum += 1
    else:
      if self.stack[0] == self.stack[1]:
        self.lineNum += 1
  
  def _cmd_jump(self, value):
    if '.' not in value and self._format_value(value) in self.labels:
      self.lineNum = self.labels[self._format_value(value)]

  def _cmd_swap(self, value):
    if value:
      value = self._format_value(value)
      self.stack[0], self.stack[value] = self.stack[value], self.stack[0]
    else:
      self.stack[0], self.stack[1] = self.stack[1], self.stack[0]
    
  def _add_label(self, value, ln):
    if '.' not in value:
      self.labels[self._format_value(value)] = ln

  def _error(self, message):
    raise twocolError(f'line {self.lineNum}: {message}')


# Main method (run from command line)
def main():
  if sys.argv:
    if os.path.isfile(sys.argv[1]):
      debug = False
      if '-d' in sys.argv:
        debug = True
      tc = TwocolInterpreter(debug=debug)
      tc.interpret(sys.argv[1])
    else:
      raise FileNotFoundError(f'Could not find file: {sys.argv[1]}')

if __name__ == '__main__':
  main()
