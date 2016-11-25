from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.portletpage.browser.interfaces import IManagePortletPagePortletsView
from collective.portletpage.interfaces import IPortletPageColumn
from plone.app.portlets.browser.manage import ManageContextualPortlets
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.memoize.instance import memoize
from zope.component import adapts, getMultiAdapter
from zope.interface import implementsOnly, Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class PortletPageColumn(ColumnPortletManagerRenderer):
    """Render a column
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IPortletPageColumn)
    template = ViewPageTemplateFile('portletpage-column.pt')

    @memoize
    def plone_view(self):
        return getMultiAdapter((self.context, self.request), name=u"plone")

    def update(self):
        super(PortletPageColumn, self).update()
        self.ids = set()

    def portlet_id(self, portlet):
        plone_view = self.plone_view()

        normal_manager = plone_view.normalizeString(self.manager.__name__)
        normal_title = plone_view.normalizeString(portlet['assignment'].title)

        while normal_title in self.ids:
            normal_title += '-x'
        self.ids.add(normal_title)

        return 'column-%s-portlet-%s' % (normal_manager, normal_title)


class ManagePortlets(ManageContextualPortlets):
    """View used for the edit screen
    """
    implementsOnly(IManagePortletPagePortletsView)

    __call__ = ViewPageTemplateFile('manage-portletpage-portlets.pt')

    def __init__(self, context, request):
        # Skip past the main parent constructor, since it sets disable_border
        super(ManageContextualPortlets, self).__init__(context, request)
