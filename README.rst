=========================
split-ebooks-into-folders
=========================
Split the supplied ebook files (and the accompanying metadata files if present) into folders with consecutive names where each contains the specified number of files.

This is a Python port of `split-into-folders.sh 
<https://github.com/na--/ebook-tools/blob/master/split-into-folders.sh>`_ from `ebook-tools 
<https://github.com/na--/ebook-tools>`_ written in shell by `na-- <https://github.com/na-->`_.

`:star:` Other related projects based on ``ebook-tools``:

- `convert-to-txt <https://github.com/raul23/convert-to-txt>`_: convert documents (pdf, djvu, epub, word) to txt
- `find-isbns <https://github.com/raul23/find-isbns>`_: find ISBNs from ebooks (pdf, djvu, epub) or any string given as input to the script
- `ocr <https://github.com/raul23/ocr>`_: run OCR on documents (pdf, djvu, and images)

|

.. contents:: **Contents**
   :depth: 3
   :local:
   :backlinks: top
   
Dependencies
============
This is the environment on which the script `split_into_folders.py <./split_into_folders/scripts/split_into_folders.py>`_ was tested:

* **Platform:** macOS
* **Python**: version **3.7**

Installation
============
To install the `split_into_folders <./split_into_folders/>`_ package::

 $ pip install git+https://github.com/raul23/split-ebooks-into-folders#egg=split-ebooks-into-folders
 
**Test installation**

1. Test your installation by importing ``split_into_folders`` and printing its
   version::

   $ python -c "import split_into_folders; print(split_into_folders.__version__)"

2. You can also test that you have access to the ``split_into_folders.py`` script by
   showing the program's version::

   $ split_into_folders --version

Uninstall
=========
To uninstall the `split_into_folders <./split_into_folders/>`_ package::

 $ pip uninstall split-ebooks-into-folders

Script options
==============
To display the script `split_into_folders.py <./split_into_folders/scripts/split_into_folders.py>`_ list of options and their descriptions::

   $ split_into_folders -h
   usage: split_into_folders [OPTIONS] {folder_with_books} [{output_folder}]

   Split the supplied ebook files (and the accompanying metadatafiles if present) into folders with consecutive names 
   that each contain the specified number of files.
   This script is based on the great ebook-tools written in shell by na-- (See https://github.com/na--/ebook-tools).

   General options:
     -h, --help                                  Show this help message and exit.
     -v, --version                               Show program's version number and exit.
     -q, --quiet                                 Enable quiet mode, i.e. nothing will be printed.
     --verbose                                   Print various debugging information, e.g. print traceback when there is an exception.
     -d, --dry-run                               If this is enabled, no file rename/move/symlink/etc. operations will actually be executed.
     -r, --reverse                               If this is enabled, the files will be sorted in reverse (i.e. descending) order. By default, 
                                                 they are sorted in ascending order.
     --log-level {debug,info,warning,error}      Set logging level. (default: info)
     --log-format {console,only_msg,simple}      Set logging formatter. (default: only_msg)

   Split options:
     -s, --start-number START_NUMBER             The number of the first folder. (default: 0)
     -f, --folder-pattern PATTERN                The print format string that specifies the pattern with which new folders will be created. 
                                                 By default it creates folders like 00000000, 00001000, 00002000, ..... (default: %05d000)
     --fpf, --files-per-folder FILES_PER_FOLDER  How many files should be moved to each folder. (default: 100)

   Input and output options:
     --ome, --output-metadata-extension EXTENSION  This is the extension of the metadata file associated with an ebook. (default: meta)
     folder_with_books                             Folder with books which will be recursively scanned for files. The found files (and the 
                                                   accompanying metadata files if present) will be split into folders with consecutive names 
                                                   that each contain the specified number of files.
     -o, --output-folder PATH                      The output folder in which all the new consecutively named folders will be created. The 
                                                   default value is the current working directory. 
                                                   (default: /Users/test/split_into_folders/test_installation)

`:information_source:` Explaining some of the options/arguments

- ``-d, --dry-run`` is a very useful option to simulate how the files will be moved, i.e. the number of folders needed to
  split them and their names. No moving operations will actually be executed.
- ``-o, --output-folder`` uses by default the working directory under which the script is running to move all the files.

Example: split 1000 ebooks into folders containing 15 each
==========================================================
Through the script ``split_into_folders.py``
--------------------------------------------

Through the API
---------------

