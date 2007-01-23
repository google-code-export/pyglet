'''Parses a requirements document.

Implementation Notes
--------------------

Ported from Alex Holkner's original code. This code is now concerned
purely with modelling what components are implemented, and to what 
degree. 
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import docutils.nodes
import docutils.parsers.rst
import re


class RequirementsComponent(object):
    FULL = 50
    DEVELOPER = 40
    PARTIAL = 25
    NONE = 0
    UNKNOWN = -1

    def __init__(self, section, name):
        self.section = section
        self.name = name
        self.progress = {}

    def set_progress(self, capability, progress):
        self.progress[capability] = progress

    def get_absname(self):
        return '%s.%s' % (self.section.get_absname(), self.name)

    def get_progress(self, capabilities):
        '''Return the progress of this component for a given set of
           capabilities.  If no capabilities match, we assume that
           they are unspecified, and return the best progress
           for any capability.'''
        for capability in capabilities:
            if capability in self.progress:
                return self.progress[capability]
        # None match, so return highest.
        return max(self.progress.values())

    def is_implemented(self, capabilities, level):
        for cap in capabilities:
            if self.progress.get(cap, self.UNKNOWN) >= level:
                return True
        return False

    def get_module_filename(self, root=''):
        path = os.path.join(*self.get_absname().split('.'))
        return '%s.py' % os.path.join(root, path)

    def get_module(self, root=''):
        name = 'tests.%s' % self.get_absname()
        module = __import__(name)
        for c in name.split('.')[1:]:
            module = getattr(module, c)
        return module

    def get_regression_image_filename(self):
        return os.path.join(regressions_path, '%s.png' % self.get_absname())

    def __repr__(self):
        return 'RequirementsComponent(%s)' % self.get_absname()

    def __str__(self):
        return self.get_absname()

    def __cmp__(self, other):
        return cmp(str(self), str(other))

class RequirementsSection(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.description = ''
        self.sections = {}
        self.components = {}
        self.all_components = []
        self.all_sections = []

    def add_section(self, section):
        self.sections[section.name] = section

    def get_section(self, name):
        if '.' in name:
            root, path = name.split('.', 1)
            section = self.sections.get(root, None)
            if section:
                return section.get_section(path)
        else:
            return self.sections.get(name, None)

    def add_component(self, component):
        assert component.section is self
        self.components[component.name] = component

    def get_component(self, name):
        section, component = name.rsplit('.', 1)
        section = self.get_section(section)
        if section:
            return section.components.get(component, None)

    def get_all_components(self):
        if not self.all_components:
            self.all_components = self.components.values()
            for section in self.sections.values():
                self.all_components += section.get_all_components()
        return self.all_components

    def get_all_sections(self): 
        if not self.all_sections:
            self.all_sections = self.sections.values()
            for section in self.sections.values():
                self.all_sections += section.get_all_sections()
        return self.all_sections

    def search(self, query):
        pattern = re.compile(query, re.I)
        results = []
        for component in self.get_all_components():
            if pattern.search(component.get_absname()):
                results.append(component)

        for section in self.get_all_sections():
            if pattern.search(section.get_absname()):
                results += section.get_all_components()

        return results
    
    def get_absname(self):
        names = []
        me = self
        while me and me.name:
            names.insert(0, me.name)
            me = me.parent
        return '.'.join(names)
        
    def __repr__(self):
        return 'RequirementsSection(%s)' % self.get_absname()

class Requirements(RequirementsSection):
    def __init__(self):
        super(Requirements, self).__init__(None, '')


class RequirementsParser(docutils.nodes.GenericNodeVisitor):
    def __init__(self, document, requirements):
        docutils.nodes.GenericNodeVisitor.__init__(self, document)

        self.requirements = requirements
        self.section_stack = [requirements]
        self.field_key = None

    def get_section(self):
        return self.section_stack[-1]

    def default_visit(self, node):
        pass

    def default_departure(self, node):
        pass

    def visit_term(self, node):
        section = RequirementsSection(self.get_section(), node.astext())
        self.get_section().add_section(section)
        self.section_stack.append(section)

    def depart_definition_list_item(self, node):
        self.section_stack.pop()

    def visit_field_name(self, node):
        self.field_key = node.astext()

    def visit_field_body(self, node):
        if self.field_key == 'description':
            self.get_section().description = node.astext()
        elif self.field_key == 'implementation':
            parser = ImplementationParser(self.document, self.get_section())
            node.walkabout(parser)

class ImplementationParser(docutils.nodes.GenericNodeVisitor):
    progress_lookup = {
        'X': RequirementsComponent.FULL,
        'D': RequirementsComponent.DEVELOPER,
        '/': RequirementsComponent.PARTIAL,
        '': RequirementsComponent.NONE,
    }

    def __init__(self, document, section):
        docutils.nodes.GenericNodeVisitor.__init__(
            self, document)
        self.section = section
        self.capabilities = []

    def default_visit(self, node):
        pass

    def default_departure(self, node):
        pass

    def visit_row(self, node):
        entries = [n.astext() for n in node.children]
        if node.parent.tagname == 'thead':
            # Head row; remember names of capabilities for this table.
            self.capabilities = entries[1:]
        else:
            component = RequirementsComponent(self.section, entries[0])
            self.section.add_component(component)
            for capability, progress in zip(self.capabilities, entries[1:]):
                progress = self.progress_lookup.get(progress.strip(),    
                               RequirementsComponent.UNKNOWN)
                component.set_progress(capability, progress)

def parse(text):
    """ Parse the given string as a requirements document.
        Returns a RequirementsDocument object.
    """
    result = Requirements()
    parser = docutils.parsers.rst.Parser()
    document = docutils.utils.new_document('requirements')
    document.settings.tab_width = 4
    document.settings.report_level = 1
    document.settings.pep_references = 1
    document.settings.rfc_references = 1
    parser.parse(text, document)
    document.walkabout(RequirementsParser(document, result))
    return result
