import unittest

from StringIO import StringIO

from rexparse import  Requirement, Requirements


class TestRequirement(unittest.TestCase):
    def test_url(self):
        self.assertTrue(Requirement(
            'http://github.com/gregbanks/rexparse/archive/master.zip').is_url)
        self.assertTrue(Requirement(
            'git+ssh://git@github.com/gregbanks/rexparse.git@master').is_url)
        self.assertFalse(Requirement('rexparse==0.1.0').is_url)

    def test_trailing_comments(self):
        self.assertEqual('rexparse==0.1.0',
                         Requirement('rexparse==0.1.0  ## blah #')._req)

    def test_version(self):
        self.assertEqual(
            '0.1.0',
             Requirement('git+ssh://git@github.com/gregbanks/rexparse.git'
                         '@master#egg=rexparse-0.1.0').version)
        self.assertIsNone(
             Requirement('git+ssh://git@github.com/gregbanks/rexparse.git'
                         '@master#egg=rexparse').version)
        self.assertIsNone(
             Requirement('git+ssh://git@github.com/gregbanks/'
                         'rexparse.git').version)
        self.assertIsNone(
             Requirement('https://github.com/gregbanks/rexparse/archive/'
                         '1.0.1.zip').version)
        self.assertEqual(
            '1',
             Requirement('git+ssh://git@github.com/gregbanks/rexparse.git'
                         '@master#egg=rexparse-1').version)
        self.assertEqual('1',
                         Requirement('rexparse==1').version)
        self.assertIsNone(Requirement('rexparse').version)


    def test_req_no_egg(self):
        self.assertIsNone(Requirement('rexparse').egg)
        self.assertIsNone(
             Requirement('https://github.com/gregbanks/rexparse/archive/'
                         '1.0.1.zip').egg)
        self.assertIsNone(
             Requirement('https://github.com/gregbanks/rexparse/archive/'
                         '1.0.1.zip').version)

    def test_dependency_link(self):
        self.assertIsNone(Requirement('rexparse').dependency_link)
        self.assertIsNotNone(
             Requirement('https://github.com/gregbanks/rexparse/archive/'
                         '1.0.1.zip').dependency_link)

    def test_egg(self):
        req = Requirement('git+ssh://git@github.com/gregbanks/rexparse.git'
                          '@master#egg=rex-parse-1.1')
        self.assertEqual('1.1', req.version)
        self.assertEqual('rex-parse', req.name)

        req = Requirement('git+ssh://git@github.com/gregbanks/rexparse.git'
                          '@master#egg=rex-parse-1.a.1')
        self.assertIsNone(req.version)
        self.assertIsNone(req.name)

    def test_transport(self):
        self.assertEqual(
            'ssh',
             Requirement('git+ssh://git@github.com/gregbanks/rexparse.git'
                         '@master#egg=rexparse-0.1.0').transport)
        self.assertEqual(
            'https',
             Requirement('https://github.com/gregbanks/rexparse/archive/'
                         'rexparse-0.1.0.zip').transport)
        self.assertIsNone(Requirement('rexparse').transport)

    def test_vcs(self):
        self.assertEqual(
            'git',
             Requirement('git+ssh://git@github.com/gregbanks/rexparse.git'
                         '@master#egg=rexparse-0.1.0').vcs)
        self.assertEqual(
            'svn',
             Requirement('svn+ssh://svnhub.com/gregbanks/rexparse'
                         '@53#egg=rexparse-0.1.0').vcs)
        self.assertIsNone(
             Requirement('https://github.com/gregbanks/rexparse/archive/'
                         'rexparse-0.1.0.zip').vcs)
        self.assertIsNone(Requirement('rexparse==0.1.0').vcs)

    def test_vcs_revision(self):
        self.assertEqual(
            'master',
             Requirement('git+ssh://git@github.com/gregbanks/rexparse.git'
                         '@master#egg=rexparse-0.1.0').vcs_revision)
        self.assertEqual(
            '53',
             Requirement('svn+ssh://svnhub.com/gregbanks/rexparse'
                         '@53#egg=rexparse-0.1.0').vcs_revision)
        self.assertIsNone(
             Requirement('https://github.com/gregbanks/rexparse/archive/'
                         'rexparse-0.1.0.zip').vcs_revision)
        self.assertIsNone(Requirement('rexparse==0.1.0').vcs_revision)


class TestRequirements(unittest.TestCase):
    def test_default_section(self):
        req_file = StringIO("blah")
        reqs = Requirements(req_file)
        reqs.parse()
        self.assertEqual(1, len(reqs.install_reqs))
        self.assertEqual(0, len(reqs.test_reqs))

    def test_change_default_section(self):
        req_file = StringIO("blah")
        reqs = Requirements(req_file, default_section='test')
        reqs.parse()
        self.assertEqual(0, len(reqs.install_reqs))
        self.assertEqual(1, len(reqs.test_reqs))

    def test_change_sections(self):
        req_file = StringIO("""
                            blah

                            # test

                            blah2
                            blah3
                            # test
                            blah4 # blah blah blah
                            # install
                            blah5
                            """)
        reqs = Requirements(req_file)
        reqs.parse()
        self.assertEqual(2, len(reqs.install_reqs))
        self.assertEqual(3, len(reqs.test_reqs))

    def test_dependency_links(self):
        req_file = StringIO(
            """
            git+ssh://git@github.com/gregbanks/rexparse.git#egg=rexparse
            https://github.com/gregbanks/rexparse/archive/master.zip#egg=rexparse

            # test
            svn+https://svnhub.com/gregbanks/rexparse@53#egg=rexparse

            # install
            blah
            """)
        reqs = Requirements(req_file)
        reqs.parse()
        self.assertEqual(3, len(reqs.install_reqs))
        self.assertEqual(1, len(reqs.test_reqs))
        self.assertEqual(3, len(reqs.dependency_links))
