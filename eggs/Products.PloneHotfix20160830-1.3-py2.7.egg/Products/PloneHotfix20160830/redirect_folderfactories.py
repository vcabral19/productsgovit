from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.folderfactories import FolderFactoriesView


def FolderFactoriesView___call__(self):
    if 'form.button.Add' in self.request.form:
        urltool = getToolByName(self.context, 'portal_url')
        url = self.request.form.get('url')
        if not urltool.isURLInPortal(url):
            url = self.context.absolute_url()
        self.request.response.redirect(url)
        return ''
    else:
        return self.index()


FolderFactoriesView.__call__ = FolderFactoriesView___call__
