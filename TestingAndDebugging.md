I've been doing some debugging and testing in pyglet and I wanted to collect a few things here.

## Debugging ##
Pyglet offers some debugging methods built into the library which are described [in the programming guide](http://www.pyglet.org/doc/programming_guide/debugging_tools.html).


## Testing ##
Pyglet also contains a test suite, which exists in the tests/ folder of the source distribution.  The test system has a number of options, more complete documentation is available in the [source file](http://code.google.com/p/pyglet/source/browse/tests/test.py).

Of immediate interest is that the tests are interactive.  There are many variations of hardware and drivers so testing involves some visual inspection.

By default, the test suite prompts for input before running each visual test, and then prompts for results after.  This behavior can be changed by passing the `--no-interactive` parameter to test.py on the command line.  To progress to the next visual test, you can hit the escape key.  Non-visual tests run automatically.

Additionally, there is a file tests/plan.txt that can be used to specify which tests are run.  You can also pass the test.py script a custom plan file, using the parameter `--plan=planfile.txt`

## Run Tests in Sections ##
Because the tests are interactive, they can take quite a while to complete. The 'window' section in particular takes a long time. It can be frustrating to get almost through the tests and then something gets messed up, so we suggest you run the tests in sections (if you are curious, the sections are defined in tests/plan.txt), e.g.
```
    python tests/test.py font
```
Here are the different sections and how long they take.

| **Section** | **Time to Run** |
|:------------|:----------------|
| top | automatic |
| app | automatic |
| graphics | automatic |
| clock | automatic |
| resource | automatic |
| font | 1 minute |
| media | 1 minute |
| text | 1 minute |
| image | 5 minutes |
| window | 10 minutes |

Here is a nice grouping that doesn't take too long for each group:
```
    python tests/test.py top app graphics clock resource # these all run automatically
    python tests/test.py font media text
    python tests/test.py image
    python tests/test.py window
```

### Adding a new test ###

There are two main steps to add a new test to the system.  Some familiarity with the python unittest framework is useful, but shouldn't be too hard to follow.


First, modify the plan.txt file to include your test.  The configuration relies on a section per test directory, and then possible sub-section, then the actual tests identified by section.FILENAME without the .py file extension.

For example this section:
```
newsection
    newsection-subsection
        newsection.FOOTEST                X11 WIN OSX
```

corresponds to the source file location /tests/newsection/FOOTEST.py, and the X11 WIN OSX entries mean to test on all three supported platforms.  You can target specific platforms exclusively or in combination as well.

Then, create this file on the filesystem.  There are some boilerplate portions of the test:

```
#!/usr/bin/env python

""" Some sort of description of the test. """
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import unittest

__noninteractive = True

class FOOTEST(unittest.TestCase):
    # unittest requires that tests be methods on the function starting with 'test'
    def test_FOO(self):
        #throw an exception if you fail
        pass
        
if __name__ == '__main__':
    unittest.main()
```