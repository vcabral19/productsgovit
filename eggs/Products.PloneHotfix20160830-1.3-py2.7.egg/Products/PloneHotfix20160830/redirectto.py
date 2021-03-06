from Products.CMFCore.utils import getToolByName
from Products.CMFFormController.Actions import RedirectTo as OrigRedirectTo
from Products.CMFFormController.Actions.BaseFormAction import BaseFormAction
from Products.CMFFormController.FormController import registerFormAction
from urlparse import urljoin
from urlparse import urlparse


def factory(arg):
    """Create a new redirect-to action"""
    return RedirectTo(arg)


class RedirectTo(BaseFormAction):

    def __call__(self, controller_state):
        url = self.getArg(controller_state)
        context = controller_state.getContext()
        # see if this is a relative url or an absolute
        if len(urlparse(url)[1]) == 0:
            # No host specified, so url is relative.  Get an absolute url.
            url = urljoin(context.absolute_url() + '/', url)
        elif not getToolByName(context, 'portal_url').isURLInPortal(url):
            url = context.absolute_url()
        url = self.updateQuery(url, controller_state.kwargs)
        request = context.REQUEST
        # this is mostly just for archetypes edit forms...
        if 'edit' in url and '_authenticator' not in url and \
                '_authenticator' in request.form:
            if '?' in url:
                url += '&'
            else:
                url += '?'
            auth = request.form['_authenticator']
            if isinstance(auth, list):
                auth = auth[0]
            url += '_authenticator=' + auth
        return request.RESPONSE.redirect(url)

registerFormAction(
    'redirect_to',
    factory,
    'Redirect to the URL specified in the argument (a TALES expression). '
    'The URL can either be absolute or relative and must be internal.')

# We register the original one under a new name,
# to make it easier for anyone who needs this.
registerFormAction(
    'external_redirect_to',
    OrigRedirectTo.factory,
    'Redirect to the URL specified in the argument (a TALES expression). '
    'The URL can either be absolute or relative, and may be external.')
