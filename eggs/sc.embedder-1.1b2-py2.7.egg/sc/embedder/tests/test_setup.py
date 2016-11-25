# -*- coding: utf-8 -*-
from plone import api
from plone.browserlayer.utils import registered_layers
from sc.embedder.config import PROJECTNAME
from sc.embedder.testing import INTEGRATION_TESTING

import unittest


class InstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']

    def test_installed(self):
        self.assertTrue(self.qi.isProductInstalled(PROJECTNAME))

    def test_browserlayer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IEmbedderLayer', layers)

    def test_css_registry(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        self.assertIn('embedder.css', resource_ids)

    def test_add_permissions(self):
        permission = 'sc.embedder: Add Embedder'
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        expected = ['Contributor', 'Manager', 'Owner', 'Site Administrator']
        self.assertListEqual(roles, expected)

    def test_tile(self):
        tiles = api.portal.get_registry_record('plone.app.tiles')
        self.assertIn(u'sc.embedder', tiles)


class UninstallTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_browserlayer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IEmbedderLayer', layers)

    def test_css_removed(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        self.assertNotIn('embedder.css', resource_ids)

    def test_tile_removed(self):
        tiles = api.portal.get_registry_record('plone.app.tiles')
        self.assertNotIn(u'sc.embedder', tiles)
