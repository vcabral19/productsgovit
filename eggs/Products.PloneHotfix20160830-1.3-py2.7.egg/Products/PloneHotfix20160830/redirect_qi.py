from Products.CMFCore.utils import getToolByName
from Products.CMFQuickInstallerTool.QuickInstallerTool import QuickInstallerTool

original_installProducts = QuickInstallerTool.installProducts


def QuickInstallerTool_installProducts(self, products=None, stoponerror=True,
                                       reinstall=False, REQUEST=None,
                                       forceProfile=False, omitSnapshots=True):
    """Install products."""
    result = original_installProducts(
        self, products=products, stoponerror=stoponerror,
        reinstall=reinstall, REQUEST=REQUEST,
        forceProfile=forceProfile, omitSnapshots=omitSnapshots)
    # check if redirect done and see if in portal...
    if REQUEST:
        resp = REQUEST.RESPONSE
        url = resp.headers.get('location')
        urltool = getToolByName(self, 'portal_url')
        if url and not urltool.isURLInPortal(url):
            resp.headers['location'] = self.absolute_url()
    return result


QuickInstallerTool.installProducts = QuickInstallerTool_installProducts
