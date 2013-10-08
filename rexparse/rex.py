import re
import string
import urlparse


PKG_PATH_RE = re.compile(r'^((?P<name>[\w-]+)(?P<version>-[\d.]+)?'
                         r'(?P<extention>[\w.]+)?)(@(?P<revision>.+))?$')
PKG_RE = re.compile(r'^(?P<name>[\w-]+)((?P<comparator>>|<|==|<=|>=)'
                    r'(?P<version>[\d.]+))?$')
EGG_RE = re.compile(r'(?i)^egg=(?P<name>[\w-]+)(-(?P<version>([a-z])?[\d.]+[a-z]*))?$')

DEFAULT_INSTALL_SECTION_RE = r'(?i)^#.*install.*'
DEFAULT_TEST_SECTION_RE = r'(?i)^#.*test.*'


def _strip_comments(line):
    index = line.find(' #')
    return line[:index].strip() if index != -1 else line


class Requirement(object):
    def __init__(self, line):
        line = _strip_comments(line)
        self.option = None
        self._req = None
        if line.startswith('-'):
            self.option, self._req = line.split()
        else:
            self._req = line

    @property
    def req(self):
        if not self.is_url:
            return self._req
        if self.egg is None:
            raise ValueError('egg required in %s to generate a requirement' %
                             (self._req))
        req = self.egg['name']
        if self.egg['version'] is not None:
            req += '==' + self.egg['version']
        return req

    @property
    def dependency_link(self):
        if not self.is_url:
            return None
        return self._req

    @property
    def is_url(self):
        return '://' in self._req

    @property
    def egg(self):
        if not self.is_url:
            return None
        parts = urlparse.urlparse(self._req)
        fragment = parts.fragment
        if len(parts.fragment) == 0:
            if not '#' in parts.path:
                return None
            fragment = parts.path.split('#')[1]
        match = EGG_RE.match(fragment)
        return None if match is None else match.groupdict()

    @property
    def transport(self):
        if not self.is_url:
            return None
        parts = urlparse.urlparse(self._req)
        return parts.scheme.split('+')[-1]

    @property
    def vcs(self):
        if not self.is_url:
            return None
        parts = urlparse.urlparse(self._req)
        if '+' not in parts.scheme:
            return None
        return parts.scheme.split('+')[0]

    @property
    def vcs_revision(self):
        if not self.is_url:
            return None
        parts = urlparse.urlparse(self._req)
        if '@' not in parts.path:
            return None
        path = parts.path.split('#')[0] if '#' in parts.path \
                                        else parts.path
        return path.split('@')[-1]

    def _get_egg_attr(self, attr):
        if not self.is_url:
            match = PKG_RE.match(self._req)
            if match is None:
                raise ValueError('req is not a url and not a package: %s' %
                                 (self._req))
            return match.group(attr)
        if self.egg is not None:
            if self.egg[attr] is not None:
                return self.egg[attr]
            elif attr == 'version':
                if ('-' in self.egg['name'] and
                    all([c in string.digits
                         for c in self.egg['name'].rsplit('-', 1)[-1]])):
                    return self.egg['name'].rsplit('-', 1)[-1]
        parts = urlparse.urlparse(self._req)
        match = PKG_PATH_RE.match(parts.path)
        return None if match is None else match.group(attr)

    @property
    def name(self):
        return self._get_egg_attr('name')

    @property
    def version(self):
        return self._get_egg_attr('version')


class Requirements(object):
    def __init__(self, requirements='requirements.txt',
                 default_section='install',
                 install_section_re=DEFAULT_INSTALL_SECTION_RE,
                 test_section_re=DEFAULT_TEST_SECTION_RE, parse=False):
        self.requirements = requirements
        if isinstance(self.requirements, basestring):
            self.requirements = open(self.requirements)
        self.sections = {'install':
                            {'regex': re.compile(install_section_re),
                             'reqs': []},
                          'test':
                             {'regex': re.compile(test_section_re),
                              'reqs': []}}
        self.cur_section = self.sections[default_section]
        self._parsed = False
        if parse:
            self.parse()

    @property
    def install_requires(self):
        return [r.req for r in self.sections['install']['reqs']]

    @property
    def tests_require(self):
        return [r.req for r in self.sections['test']['reqs']]

    @property
    def dependency_links(self):
        return filter(None,
                      [r.dependency_link for r in
                       self.sections['install']['reqs']] +
                      [r.dependency_link for r in self.sections['test']['reqs']])

    def parse(self):
        if self._parsed:
            return
        for line in self.requirements:
            line = line.strip()
            if len(line) == 0:
                continue
            section_matches = [s for s in self.sections
                               if self.sections[s]['regex'].match(line)
                                  is not None]
            if len(section_matches) == 1:
                self.cur_section = self.sections[section_matches[0]]
                continue
            elif len(section_matches) > 1:
                raise RuntimeError('multiple section separators (%s)'
                                   'matched requirements file line %s' %
                                   (str(section_matches), line))
            self.cur_section['reqs'].append(Requirement(line))
        self._parsed = True

