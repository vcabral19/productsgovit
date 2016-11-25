from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import url_unquote
from zope.component import getMultiAdapter
try:
    from plone.app.portlets.browser.formhelper import AddForm
    from plone.app.portlets.browser.formhelper import EditForm
    from plone.app.portlets.browser.formhelper import NullAddForm
    from plone.app.portlets.browser.adding import PortletAdding
    from plone.app.portlets.browser.editmanager import ManagePortletAssignments
except ImportError:
    AddForm = None
    EditForm = None
    NullAddForm = None
    PortletAdding = None
    ManagePortletAssignments = None


try:
    from plone.app.portlets.browser import z3cformhelper
except ImportError:
    z3cformhelper = None


def PortletAdding_nextURL(self):
    referer = self.request.get('referer')
    urltool = getToolByName(self.context, 'portal_url')
    if not referer or not urltool.isURLInPortal(referer):
        context = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        referer = url + '/@@manage-portlets'
    return referer
if hasattr(PortletAdding, 'nextURL'):
    PortletAdding.nextURL = PortletAdding_nextURL


def ManagePortletAssignments_nextUrl(self):
    referer = self.request.get('referer')
    urltool = getToolByName(self.context, 'portal_url')
    if referer:
        referer = url_unquote(referer)

    if not referer or not urltool.isURLInPortal(referer):
        context = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        referer = '%s/@@manage-portlets' % (url,)
    return referer
if hasattr(ManagePortletAssignments, '_nextUrl'):
    ManagePortletAssignments._nextUrl = ManagePortletAssignments_nextUrl


def AddForm_nextURL(self):
    urltool = getToolByName(self.context, 'portal_url')
    # Some versions don't have this (early z3cform helper in Plone 4.2.)
    referer = getattr(self, 'referer', None)
    if callable(referer):
        # Some versions have this as @property, some not.
        referer = referer()
    if referer and urltool.isURLInPortal(referer):
        return referer
    addview = aq_parent(aq_inner(self.context))
    context = aq_parent(aq_inner(addview))
    try:
        url = str(getMultiAdapter((context, self.request),
                                  name=u"absolute_url"))
    except (TypeError, AttributeError):
        url = self.context.absolute_url()
    return url + '/@@manage-portlets'
if hasattr(AddForm, 'nextURL'):
    AddForm.nextURL = AddForm_nextURL
if hasattr(EditForm, 'nextURL'):
    EditForm.nextURL = AddForm_nextURL
if hasattr(NullAddForm, 'nextURL'):
    NullAddForm.nextURL = AddForm_nextURL


if z3cformhelper is not None:
    z3cformhelper.AddForm.nextURL = AddForm_nextURL
    z3cformhelper.EditForm.nextURL = AddForm_nextURL
