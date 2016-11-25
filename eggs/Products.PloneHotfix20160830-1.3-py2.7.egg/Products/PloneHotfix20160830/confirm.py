from plone.protect.views import ConfirmView
from Products.CMFCore.utils import getToolByName
from zExceptions import Forbidden


def ConfirmView__call__(self):
    urltool = getToolByName(self.context, 'portal_url')
    original_url = getattr(self.request, 'original_url', '')
    if not original_url or not urltool.isURLInPortal(original_url):
        raise Forbidden('url not in portal')
    return self.index()


ConfirmView.__call__ = ConfirmView__call__
