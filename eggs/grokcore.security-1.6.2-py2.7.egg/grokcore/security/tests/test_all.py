import re
import unittest
from pkg_resources import resource_listdir
from zope.testing import doctest, cleanup, renormalizing

def cleanUpZope(test):
    cleanup.cleanUp()

checker = renormalizing.RENormalizing([
    # str(Exception) has changed from Python 2.4 to 2.5 (due to
    # Exception now being a new-style class).  This changes the way
    # exceptions appear in traceback printouts.
    (re.compile(
        r"ConfigurationExecutionError: <class '([\w.]+)'>:"),
        r'ConfigurationExecutionError: \1:'),
        ])

def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue
        dottedname = 'grokcore.security.tests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname,
            tearDown=cleanUpZope,
            checker=checker,
            optionflags=doctest.ELLIPSIS+
            doctest.NORMALIZE_WHITESPACE)
        suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    for name in [
        'permissions',
        'role',
        'security',
        ]:
        suite.addTest(suiteFromPackage(name))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
