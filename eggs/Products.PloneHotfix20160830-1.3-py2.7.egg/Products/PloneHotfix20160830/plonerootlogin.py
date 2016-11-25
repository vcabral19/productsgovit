from Products.CMFPlone.browser.admin import RootLoginRedirect
from urlparse import urljoin
from urlparse import urlparse


def RootLoginRedirect__call__(self, came_from=None):
    # This view of the Zope root forces authentication via the root
    # acl_users and then redirects elsewhere.
    if came_from is not None:
        # see if this is a relative url or an absolute
        if len(urlparse(came_from)[1]) == 0:
            # No host specified, so url is relative.  Get an absolute url.
            # Note: '\\domain.org' is not recognised as host, which is good.
            came_from = urljoin(self.context.absolute_url() + '/', came_from)
        elif not came_from.startswith(self.context.absolute_url()):
            # Note: we cannot use portal_url.isURLInPortal here, because we are
            # not in a Plone portal, but in the Zope root.
            came_from = None
    if came_from is None:
        came_from = self.context.absolute_url()
    self.request.response.redirect(came_from)

RootLoginRedirect.__call__ = RootLoginRedirect__call__
