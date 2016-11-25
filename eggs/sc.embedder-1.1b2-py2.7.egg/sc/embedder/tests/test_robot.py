# -*- coding: utf-8 -*-
from plone.testing import layered
from sc.embedder.testing import PLONE_VERSION
from sc.embedder.testing import ROBOT_TESTING

import os
import robotsuite
import unittest


dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test_') and f.endswith('.robot')]

# skip RobotFramework tests in Plone 5
if PLONE_VERSION.startswith('5'):
    tests = []


class Keywords(object):
    """ Robot Framework keyword library """

    def get_path_to_tests(self):
        from os.path import dirname
        return dirname(__file__)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            robotsuite.RobotTestSuite(t, noncritical=['Expected Failure']),
            layer=ROBOT_TESTING)
        for t in tests
    ])
    return suite
