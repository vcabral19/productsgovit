from App.Management import Tabs
from App.special_dtml import DTMLFile
from App.special_dtml import HTMLFile
from Products.Transience.Transience import TransientObjectContainer

import Products.ExternalEditor  # noqa force this patch to be done first

# Add external editor icon in breadcrumbs under tabs
Tabs.manage_tabs = DTMLFile('www/manage_tabs', globals())
TransientObjectContainer.manage_container = HTMLFile(
    'www/manageTransientObjectContainer',
    globals())
