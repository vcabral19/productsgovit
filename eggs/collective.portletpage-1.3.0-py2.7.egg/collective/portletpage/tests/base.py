# -*- coding: utf-8 -*-

from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.bbb import PloneTestCase
from plone.app.testing.bbb import PTC_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing import z2
from zope.interface import implements
import transaction

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry

import collective.portletpage


class CollectivePortletpageLayer(PloneSandboxLayer):

    defaultBases = (PTC_FUNCTIONAL_TESTING,)

    def setUpZope(self, app, configurationContext):
        profile_registry.registerProfile('testing',
            'Collective.portletpage testing profile',
            'Extension profile including collective.portletpage testing additions',
            'profiles/testing',
            'collective.portletpage',
            EXTENSION)
        self.loadZCML('testing.zcml', package=collective.portletpage.tests)
        self.loadZCML(package=collective.portletpage)
        z2.installProduct(app, 'collective.portletpage')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.portletpage:default')
        applyProfile(portal, 'collective.portletpage:testing')


COLLECTIVE_PORTLETPAGE_FIXTURE = CollectivePortletpageLayer()
COLLECTIVE_PORTLETPAGE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PORTLETPAGE_FIXTURE,),
    name='CollectivePortletpageLayer:IntegrationTesting'
)


COLLECTIVE_PORTLETPAGE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PORTLETPAGE_FIXTURE,),
    name='CollectivePortletpageLayer:FunctionalTesting'
)


COLLECTIVE_PORTLETPAGE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_PORTLETPAGE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectivePortletpageLayer:AcceptanceTesting'
)


class IPortletPageDummy(IPortletDataProvider):
    """A portlet which can render a login form.
    """


class Assignment(base.Assignment):
    implements(IPortletPageDummy)

    title = "Dummy Portlet"


class Renderer(base.Renderer):

    available = True

    def render(self):
        return "Lorem Ipsum"


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()

class TestCase(PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

    layer = COLLECTIVE_PORTLETPAGE_FUNCTIONAL_TESTING
