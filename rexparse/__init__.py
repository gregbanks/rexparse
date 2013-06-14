import os
import re

from functools import wraps

from distutils.errors import DistutilsSetupError

from rex import Requirements, Requirement

from _version import __version__


__all__ = ['Requirements', 'Requirement', 'get_version']


def get_version(path):
    version = None
    try:
        version =  re.search(r'__version__\s*=\s*[\'"]([\d.]+)[\'"]',
                             open(path).read()).group(1)
    except (IOError, AttributeError):
        pass
    return version


def set_dist_attr(dist, attr, val):
    if not isinstance(val, Requirements):
        if not isinstance(val, basestring):
            raise DistutilsSetupError('%r must be a string, got %r' %
                                      (attr, type(val)))
        if not os.path.isfile(val):
            raise DistutilsSetupError('%s does not appear to be a file' %
                                      (val))
    if attr in ['install_requires', 'tests_require', 'dependency_links']:
        if not isinstance(val, Requirements):
            val = Requirements(val, parse=True)
        setattr(dist, attr, getattr(val, attr))
    elif attr == 'version':
        setattr(dist, attr, get_version(val))
    else:
        raise DistutilsSetupError('unknown attr %s' % (attr))


def rexparse(dist, attr, val):
    if not isinstance(val, dict):
        raise DistutilsSetupError('%s must be a dict with keys '
                                  '"requirements_path" and (optionally) '
                                  '"version_path"' % (attr))
    valid_args = set(['requirements_path', 'version_path'])
    if len(set(val.keys()) - valid_args) > 0:
        raise DistutilsSetupError('got unknown arguments %r' %
                                  (set(val.keys()) - valid_args))
    if 'version_path' in val:
        set_dist_attr(dist, 'version', val['version_path'])
    reqs = Requirements(val['requirements_path'], parse=True)
    for key in ['install_requires', 'tests_require', 'dependency_links']:
        set_dist_attr(dist, key, reqs)

