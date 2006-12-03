#!/usr/bin/env python

'''Test that a font likely to be installed on the computer can be
loaded and displayed correctly.

One window will open, it should show "Quick brown fox" at 24pt using:

  * "Helvetica" on Mac OS X
  * "Arial" on Windows

'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import unittest
import sys
import base_text

if sys.platform == 'darwin':
    font_name = 'Helvetica'
elif sys.platform == 'win32':
    font_name = 'Arial'

class TEST_SYSTEM(base_text.TextTestBase):
    font_name = font_name

if __name__ == '__main__':
    unittest.main()
