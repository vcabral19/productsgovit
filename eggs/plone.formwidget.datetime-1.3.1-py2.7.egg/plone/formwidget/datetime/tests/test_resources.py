from Products.CMFCore.utils import getToolByName
from plone.formwidget.datetime.testing import PFWDT_INTEGRATION_TESTING

import unittest2 as unittest


class DatetimeTest(unittest.TestCase):
    layer = PFWDT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_portal_js(self):
        # this plugin is disabled by default. let's check if it's now enabled'
        p_js = getToolByName(self.portal, 'portal_javascripts')
        js_id = "++resource++plone.app.jquerytools.dateinput.js"
        self.assertTrue(p_js.getResource(js_id).getEnabled())

    def test_portal_css(self):
        # this stylesheet is disabled by default. let's check if it's now enabled
        p_css = getToolByName(self.portal, 'portal_css')
        css_id = "++resource++plone.app.jquerytools.dateinput.css"
        self.assertTrue(p_css.getResource(css_id).getEnabled())

        css_id = "++resource++plone.formwidget.datetime/styles.css"
        self.assertTrue(p_css.getResource(css_id).getEnabled())
