#!/usr/bin/env python

'''Test that font colour is applied correctly.   Default font should
appear blue.  Check antialiasing carefully.
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import unittest
import base_text

class TEST_DEFAULT(base_text.TextTestBase):
    font_name = ''

    def render(self):
        self.layout = self.font.render(self.text, (0, 0, 1, 1))

if __name__ == '__main__':
    unittest.main()
