#!/usr/bin/env python -B
# coding: utf-8
import unittest
import doctest
import os
import sys
import importlib
import textwrap
import traceback
import time
import inspect
import argparse
try:
  from coverage import coverage
except:
  coverage = None

IGNORE_DIRS = {'.git', '.svn', 'CVS', '__pycache__', '.DS_Store'}
IGNORE_FILES = {'.gitignore'}
DOCTEST_FILE_TYPES = {'.txt', '.md', '.html', '.htm', ''}
CHAR_OK = u'✓' #'✔'
CHAR_FAILED = u'✗' #'✖'
CHAR_SKIP = u'-'

if sys.stdout.isatty():
  COLOR_RESET         = '\033[0m'
  COLOR_OK            = '\033[32m'
  COLOR_FAILED        = '\033[31m'
  COLOR_FAILED_2      = '\033[31;7m'
  COLOR_SKIP          = '\033[35m'
  COLOR_SKIP_2        = '\033[35;7m'
  COLOR_DOCTEST       = '\033[36m'
  COLOR_UNITTEST      = '\033[36m'
  COLOR_RESULT_OK     = '\033[32;7m'
  COLOR_COVERAGE      = '\033[7m'
  COLOR_RESULT_FAILED = '\033[33;41m'
else:
  COLOR_RESET         = ''
  COLOR_OK            = ''
  COLOR_FAILED        = ''
  COLOR_FAILED_2      = ''
  COLOR_SKIP          = ''
  COLOR_SKIP_2        = ''
  COLOR_DOCTEST       = ''
  COLOR_UNITTEST      = ''
  COLOR_COVERAGE      = ''
  COLOR_RESULT_OK     = ''
  COLOR_RESULT_FAILED = ''

PREFIX_FAILED = ' {} {}'.format(COLOR_FAILED_2, COLOR_RESET)
TERMINAL_WIDTH = 80
TERMINAL_HEIGHT = 25


attempted = 0
failed = 0
skipped = 0

def count_attempted():
  global attempted
  attempted += 1

def count_failed():
  global failed
  failed += 1

def count_skipped():
  global skipped
  skipped += 1  

  
def wrapper(text, indent = PREFIX_FAILED + '  '):
  return textwrap.wrap(text.rstrip('\n'), 
                       width=TERMINAL_WIDTH - 3, 
                       initial_indent=indent,
                       subsequent_indent=indent + '        ')


def format_exception(type_, value, tb):
  result = []
  for lines in traceback.format_exception(type_, value, tb):
    lines = lines.rstrip('\n')
    for line in lines.split('\n'):
      line = wrapper(line, ' ')
      result.append(PREFIX_FAILED + ('\n' + PREFIX_FAILED).join(line))
  return '\n'.join(result)
  

def calcTerminalSize():
  global TERMINAL_WIDTH, TERMINAL_HEIGHT
  
  def ioctl_GWINSZ(fd):
    try:
      import fcntl, termios, struct
      return struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
    except: pass
    
  cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
  if not cr:
    try:
      fd = os.open(os.ctermid(), os.O_RDONLY)
      cr = ioctl_GWINSZ(fd)
      os.close(fd)
    except: pass
      
  if not cr: cr = (os.environ.get('LINES', 25), os.environ.get('COLUMNS', 80))

  TERMINAL_WIDTH = int(cr[1])
  TERMINAL_HEIGHT = int(cr[0])

def getFilename(dirpath, filename):
  if dirpath:
    return dirpath + os.sep + filename
  else:
    return filename


last_test_name = ''
last_test_filename = ''

class DocTestRunner(doctest.DocTestRunner):
  def print_result(self, out, test, example, result):
    lineno_text = ' <line {}>'.format(test.lineno + example.lineno + 1)
    msg = example.source.rstrip('\n')
    max_width = TERMINAL_WIDTH - 4 - len(lineno_text)
    if len(msg) > max_width: msg = msg[0:max_width - 3] + '...'
    
    color = COLOR_OK
    if result != CHAR_OK: color = COLOR_FAILED
    
    out(u'{color} {flag} {msg}{color_reset}{lineno}\n'.format(
        flag=result, 
        msg=msg, 
        lineno=lineno_text, 
        color=color, 
        color_reset=COLOR_RESET))
  
  def report_start(self, out, test, example):
    global last_test_name, last_test_filename
    count_attempted()
    if last_test_name != test.name or last_test_filename != self.filename:
      last_test_name = test.name
      last_test_filename = self.filename
      filename = getFilename(self.dirpath, self.filename)
      
      msg = {
          'name': test.name, 
          'file': filename, 
          'lineno': test.lineno, 
          'color': COLOR_DOCTEST, 
          'color_reset': COLOR_RESET}
      
      name_prefix = self.dirpath.replace(os.sep, '.') + '.'
      if filename.endswith('.py') and test.name.startswith(name_prefix):
        msg['name'] = test.name[len(name_prefix):]

      out(u'{color}>>> {name} <{file}:{lineno}>{color_reset}\n'.format(**msg))
  
  def report_success(self, out, test, example, got):
    self.print_result(out, test, example, CHAR_OK)
    
  def report_failure(self, out, test, example, got):
    count_failed()
    self.print_result(out, test, example, CHAR_FAILED)
    want = '\n'.join(wrapper(example.want, '  '))
    got = '\n'.join(wrapper(got, '  '))
    out(u'{0} Expected:\n{0} {1}\n{0} Got:\n{0} {2}\n'.format(
        PREFIX_FAILED, want, got))
    
  def report_unexpected_exception(self, out, test, example, exc_info):
    count_failed()
    self.print_result(out, test, example, CHAR_FAILED)
    out(format_exception(*exc_info) + '\n')


last_testcase_class = None.__class__

class TestResult(unittest.TestResult):
  def print_result(self, result, name, lineno):
    color = COLOR_OK
    if result != CHAR_OK: color = COLOR_FAILED
    print(u'{color} {flag} {name}{color_reset} <line {lineno}>'.format(
          flag=result, 
          name=name, 
          lineno=lineno, 
          color=color, 
          color_reset=COLOR_RESET))
  
  def inspect_test(self, test):
    method_name = test._testMethodName
    class_name = test.id()[0:-len(method_name) - 1]
    method = test.__class__.__dict__[method_name]
    source, lineno = inspect.getsourcelines(method)
    return class_name, method_name, lineno
  
  def startTest(self, test):
    global last_testcase_class
    count_attempted()
    if last_testcase_class is not test.__class__:
      last_testcase_class = test.__class__
      class_name, method_name, lineno = self.inspect_test(test)
      source, lineno = inspect.getsourcelines(test.__class__)
      print(u'{color}::: {name} <{file}:{lineno}>{color_reset}'.format(
            name=test.__class__.__name__, 
            file=self.filename, 
            lineno=lineno, 
            color=COLOR_UNITTEST, 
            color_reset=COLOR_RESET))
  
  def addSuccess(self, test):
    class_name, method_name, lineno = self.inspect_test(test)
    self.print_result(CHAR_OK, method_name, lineno)
  
  def addError(self, test, err):
    count_failed()
    class_name, method_name, lineno = self.inspect_test(test)
    self.print_result(CHAR_FAILED, method_name, lineno)
    print(format_exception(*err))
  
  def addFailure(self, test, err):
    count_failed()
    class_name, method_name, lineno = self.inspect_test(test)
    self.print_result(CHAR_FAILED, method_name, lineno)
    print(format_exception(*err))
  
  def addSkip(self, test, reason):
    count_skipped()
    class_name, method_name, lineno = self.inspect_test(test)
    print('{color} {flag} SKIP: {name}{color_reset} <line {lineno}>'.format(
          flag=CHAR_SKIP, 
          name=method_name, 
          lineno=lineno, 
          color=COLOR_SKIP, 
          color_reset=COLOR_RESET))
    prefix = ' {} {} '.format(COLOR_SKIP_2, COLOR_RESET)
    print(prefix + ('\n' + prefix).join(wrapper('REASON: ' + reason, '')))
  
  def addExpectedFailure(self, test, err):
    class_name, method_name, lineno = self.inspect_test(test)
    self.print_result(CHAR_OK, 'EXPECTED FAILURE: ' + method_name, lineno)
    # print(format_exception(*err))
  
  def addUnexpectedSuccess(self, test):
    count_failed()
    class_name, method_name, lineno = self.inspect_test(test)
    self.print_result(CHAR_FAILED, 
                      'UNEXPECTED SUCCESS: ' +  method_name, 
                      lineno)
  

doctest_finder = doctest.DocTestFinder()
doctest_parser = doctest.DocTestParser()
doctest_runner = DocTestRunner()

def test_unittest(dirpath, filename, module_name, name, relpath):
  test_suite = unittest.defaultTestLoader.loadTestsFromName(module_name)
  if test_suite.countTestCases() > 0:
    test_result = TestResult()
    test_result.filename = getFilename(relpath, filename)
    test_suite.run(test_result)
  
def test_doctest_py(dirpath, filename, module_name, name, relpath):
  for test in doctest_finder.find(importlib.import_module(module_name)):
    doctest_runner.dirpath = relpath
    doctest_runner.filename = filename
    doctest_runner.run(test)

def test_doctest_nonpy(dirpath, filename, module_name, name, relpath):
  try:
    with open(os.path.join(dirpath, filename)) as f:
      string = f.read()
      result = doctest_parser.parse(string)
      examples = [x for x in result if isinstance(x, doctest.Example)]
      if len(examples) > 0:
        test = doctest.DocTest(examples, globals(), name, filename, 0, string)
        doctest_runner.dirpath = relpath
        doctest_runner.filename = filename
        doctest_runner.run(test)
  except: pass

def test_run(cwd, dirpath, filename):
  dirpath = os.path.abspath(dirpath)
  if dirpath.startswith(cwd):
    relpath = dirpath[len(cwd):].lstrip(os.sep)
    name, ext = os.path.splitext(filename)
    is_package_dir = True
    
    if relpath != '':
      module_name = relpath.replace(os.sep, '.') + '.' + name
      pathhead = relpath
      while pathhead != '':
        if not os.path.isfile(os.path.join(pathhead, '__init__.py')):
          is_package_dir = False
          break
        pathhead, pathtail = os.path.split(pathhead)
    else:
      module_name = name

    if ext == '.py' and is_package_dir:
      test_doctest_py(dirpath, filename, module_name, name, relpath)
      test_unittest(dirpath, filename, module_name, name, relpath)
    elif ext == '.py' or ext in DOCTEST_FILE_TYPES:
      test_doctest_nonpy(dirpath, filename, module_name, name, relpath)

def test_coverage_report(cov, args, cwd):
  cov.stop()
      
  if sys.stdout.isatty():
    print('{color}{msg:^{width}}{color_reset}'.format(
          msg='COVERAGE SUMMARY', 
          color=COLOR_COVERAGE, 
          color_reset=COLOR_RESET,
          width=TERMINAL_WIDTH))
  else:
    print('\nCOVERAGE SUMMARY:\n')
  cov.report()
  
  if args.coverage_save: 
    cov.save()
  
  if args.coverage_text is not None:
    cov.report(file=args.coverage_text)
    args.coverage_text.close()
  
  if args.coverage_xml is not None:
    cov.xml_report(outfile=args.coverage_xml)
  
  if args.coverage_html is not None:
    cov.html_report(directory=args.coverage_html)

def parse_arguments():
  argparser = argparse.ArgumentParser(description='Python test runner.')
  argparser.add_argument('-d', '--dir', 
                         default=os.getcwd(),
                         help='change work directory')
  argparser.add_argument('files', 
                         metavar='file', 
                         nargs='*',
                         help='testcase file name')
  if coverage is not None:
    argparser.add_argument('--without-coverage-report', 
                           action='store_true',
                           help="don't report coverage results")
    argparser.add_argument('--coverage-save', 
                           action='store_true',
                           help='save the collected coverage data to '
                                'the data file')
    argparser.add_argument('--coverage-text',
                           metavar='file', 
                           type=argparse.FileType('w'),
                           help='write a summary report to a file')
    argparser.add_argument('--coverage-html',
                           metavar='dir', 
                           help='produce annotated HTML listings with '
                                'coverage results')
    argparser.add_argument('--coverage-xml',
                           metavar='file', 
                           help='produce an XML report with coverage results')
  return argparser.parse_args()


def main():
  args = parse_arguments()
  
  cwd = os.path.abspath(args.dir)
  sys.dont_write_bytecode = True
  
  if not args.without_coverage_report and coverage is not None:
    cov = coverage(omit=[sys.argv[0]])
    cov.start()
  
  start_time = time.time()
  
  calcTerminalSize()
  sys.path.insert(0, cwd)
  
  if len(args.files) > 0:
    for filename in args.files:
      filename = os.path.normpath(os.path.join(cwd, filename))
      if os.path.isfile(filename):
        test_run(cwd, os.path.dirname(filename), os.path.basename(filename))
      else:
        print(u'{color}*** {name}: No such file {color_reset}'.format(
              name=filename, 
              color=COLOR_FAILED, 
              color_reset=COLOR_RESET))
  else:
    os.chdir(cwd)
    for dirpath, dirnames, filenames in os.walk(cwd):
      for ignore_dir in IGNORE_DIRS & set(dirnames):
        dirnames.remove(ignore_dir)
      
      for ignore_file in IGNORE_FILES & set(filenames):
        filenames.remove(ignore_file)
      
      for filename in filenames:
        test_run(cwd, dirpath, filename)

  seconds = time.time() - start_time
  
  if attempted:
    if not args.without_coverage_report and coverage is not None:
      test_coverage_report(cov, args, cwd)
    
    msg = 'Ran {} tests in {:.3f}s'.format(attempted, seconds)
    
    if skipped > 0:
      msg += ', {} skipped'.format(skipped)
    
    if failed > 0:
      msg += ', {} failed'.format(failed)
      color = COLOR_RESULT_FAILED
    else:
      msg += ', all passed'
      color = COLOR_RESULT_OK
    
    if sys.stdout.isatty():
      print(u'{color}{msg:^{width}}{color_reset}'.format(
            msg=msg, 
            color=color, 
            color_reset=COLOR_RESET, 
            width=TERMINAL_WIDTH))
    else:
      print('\n' + msg + '\n')
    
    if failed > 0: sys.exit(1)
  
  
if __name__ == '__main__': main()
