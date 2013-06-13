import os

from functools import wraps

from distutils.errors import DistutilsSetupError

from rex import Requirements, Requirement

from _version import __version__


__all__ = ['Requirements', 'Requirement', 'install_requirements',
           'test_requirements', 'dependency_links']



def _check_arg(func):
    @wraps(func)
    def wrapped(dist, attr, val):
        if not isinstance(val, basestring):
            raise DistutilsSetupError('%r must be a string, got %r' %
                                      (attr, type(val)))
        if not os.path.isfile(val):
            raise DistutilsSetupError('%s does not appear to be a file' %
                                      (val))
        return func(dist, attr, val)
    return wrapped

@_check_arg
def install_requirements(dist, attr, val):
    setattr(dist, attr, Requirements(val).install_reqs)

@_check_arg
def test_requirements(dist, attr, val):
    setattr(dist, attr, Requirements(val).test_reqs)

@_check_arg
def dependency_links(dist, attr, val):
    setattr(dist, attr, Requirements(val).dependency_links)

