import os
import sys

from setuptools import setup, find_packages


setup_dir = os.path.dirname(os.path.abspath(__file__))
version = None
try:
    sys.path.insert(0, setup_dir)
    from rexparse import get_version
    version = get_version(os.path.join(setup_dir, 'rexparse', '_version.py'))
except Exception, e:
    pass
finally:
    sys.path.pop(0)


setup(name='rexparse',
      author='Greg Banks',
      author_email='quaid@kuatowares.com',
      version=version,
      install_requires=['bunch'],
      tests_require=['nose'],
      test_suite='nose.collector',
      packages=find_packages())

