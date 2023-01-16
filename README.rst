=========================
split-ebooks-into-folders
=========================
Split the supplied ebook files (and the accompanying metadata files if present) into folders with consecutive names where each contain the specified number of files.

This is a Python port of `split-into-folders.sh 
<https://github.com/na--/ebook-tools/blob/master/split-into-folders.sh>`_ from `ebook-tools 
<https://github.com/na--/ebook-tools>`_ written in shell by `na-- <https://github.com/na-->`_.

|

`:star:` Other related projects based from ``ebook-tools``:

- `convert-to-txt <https://github.com/raul23/convert-to-txt>`_: convert documents (pdf, djvu, epub, word) to txt
- `find-isbns <https://github.com/raul23/find-isbns>`_: find ISBNs from ebooks (pdf, djvu, epub) or any string given as input to the script
- `ocr <https://github.com/raul23/ocr>`_: run OCR on documents (pdf, djvu, and images)

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

 $ pip uninstall split_into_folders

Script options
==============
To display the script `split_into_folders.py <./split_into_folders/scripts/split_into_folders.py>`_ list of options and their descriptions::
