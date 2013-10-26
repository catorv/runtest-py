Python 测试执行脚本
=================
`runtest.py` 是一个简单方便但功能齐全的 Python 测试执行脚本。紧凑但结构清晰的结果报告，在`linux`、`unix`、`Mac OS`系统的终端中支持彩色文本显示，测试结果一目了然。

支持 `python 2.7.x` 和 `python 3.x`。

*注: `runtest.py` 从未在 `python 2.6.x` 以下版本中测试过，有兴趣的话你可以尝试一下，如果能告知测试及兼容性适配的结果，本人将不胜感激。*

自动执行测试
----------
1. `*.py` 文件中的 `unittest` 测试用例和 `doctest` 脚本
2. 文本文件中的 `doctest` 脚本，支持`*.txt`、`*.md`、`*.html`、`*.htm`
3. 无扩展名的文件将被当做文本文件，并尝试执行其中的 `doctest` 脚本
4. 自动忽略版本管理等特殊文件和目录

详见 `runtest.py` 源代码中的：

    IGNORE_DIRS = {'.git', '.svn', 'CVS', '__pycache__', '.DS_Store'}
    IGNORE_FILES = {'.gitignore'}
    DOCTEST_FILE_TYPES = {'.txt', '.md', '.html', '.htm', ''}

关于 `doctest` 和 `unittest`，详见Python官方文档：

* `doctest`：[Test interactive Python examples][doctest]
* `unittest`：[Unit testing framework][unittest]

[doctest]: http://docs.python.org/3.3/library/doctest.html
           "Python 官方文档的 doctest 链接"
[unittest]: http://docs.python.org/3.3/library/unittest.html
            "Python 官方文档的 unittest 链接"

安装
----
下载 `runtest.py` 文件，然后

    $ cp runtest.py /usr/local/bin/
    $ chmod +x /usr/local/bin/runtest.py

使用方法
-------
	$ runtest.py -h
	usage: runtest.py [-h] [-d DIR] [--without-coverage-report] [--coverage-save]
	                  [--coverage-text file] [--coverage-html dir]
	                  [--coverage-xml file]
	                  [file [file ...]]
	
	Python test runner.
	
	positional arguments:
	  file                  testcase file name
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -d DIR, --dir DIR     change work directory
	  --without-coverage-report
	                        don't report coverage results
	  --coverage-save       save the collected coverage data to the data file
	  --coverage-text file  write a summary report to a file
	  --coverage-html dir   produce annotated HTML listings with coverage results
	  --coverage-xml file   produce an XML report with coverage results

详细说明
-------

### 自动遍历并测试所有文件

    $ cd path/to/project
    $ runtest.py
	
或者

    $ runtest.py -d path/to/project
	
### 只测试部分文件

    $ cd path/to/project
    $ runtest.py file1.py relpath/file2.txt ...

或者
	
    $ runtest.py -d path/to/project file1.py relpath/file2.txt ...
	
### 执行测试并保存测试代码覆盖率报告

	$ runtest.py --coverage-save            # 保存到文件 .coverage 中 
	$ runtest.py --coverage-text file.txt   # 保存文本报告到 file.txt 中
	$ runtest.py --coverage-html html       # 保存HTML报告到 html 目录下
	$ runtest.py --coverage-xml report.xml  # 保存XML报告到 report.xml 中

支持测试代码覆盖率统计
------------------
`runtest.py` 通过 [coverage] 实现统计和打印测试代码覆盖率报告，并支持将结果报告保存成`data`、`text`、`html`和`xml`文件格式。

安装 [coverage] ：

    $ pip install coverage
    
或者

    $ easy_install coverage
    
详见官方网站：<http://nedbatchelder.com/code/coverage/>

*注：如果未安装 `coverage`，`runtest.py` 将自动忽略代码覆盖率统计，但其他功能仍可正常使用*

[coverage]: https://pypi.python.org/pypi/coverage
            "coverage 下载地址"

支持 Python 3.x
---------------
目前大部分系统默认安装的是 `python 2.x` 系统，以下3种方法可以让 `runtest.py` 运行在 `python 3.x` 下

    $ ln -s path/to/python3/bin/python3 /usr/bin/python

或者
    
    $ python3 runtest.py

或者将`runtest.py`文件的第一行

    #!/usr/bin/env python -B

修改为

    #!/usr/bin/env python3 -B

写在最后
-------
若有任何疑问或建议，请随时与我联系！

Don't be shy! Just email me: <catorwei@gmail.com> !