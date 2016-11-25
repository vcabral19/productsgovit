import transaction
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

# TODO: replace this with profile-only setup
#
PRODUCT_DEPENDENCIES = ['collective.js.jqueryui', 'collective.js.fullcalendar']

def checkViews(context):
    ttool = getToolByName(context, 'portal_types')
    topic_type = getattr(ttool, 'Topic', None)
    if topic_type:
        topic_methods = topic_type.view_methods
        if 'solgemafullcalendar_view' not in topic_methods:
            topic_type.view_methods=topic_methods+tuple(['solgemafullcalendar_view',])

    event_type = getattr(ttool, 'Event', None)
    if event_type:
        event_methods = event_type.view_methods
        if 'solgemafullcalendar_view' not in event_methods:
            event_type.view_methods=event_methods+tuple(['solgemafullcalendar_view',])

    folder_type = getattr(ttool, 'Folder', None)
    if folder_type:
        folder_methods = folder_type.view_methods
        if 'solgemafullcalendar_view' not in folder_methods:
            folder_type.view_methods=folder_methods+tuple(['solgemafullcalendar_view',])

    collection_type = getattr(ttool, 'Collection', None)
    if collection_type:
        collection_methods = collection_type.view_methods
        if 'solgemafullcalendar_view' not in collection_methods:
            collection_type.view_methods=collection_methods+tuple(['solgemafullcalendar_view',])

def install(self, reinstall=False):

    portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
    portal_setup = getToolByName(self, 'portal_setup')

    for product in PRODUCT_DEPENDENCIES:
        if not portal_quickinstaller.isProductInstalled(product):
            portal_quickinstaller.installProduct(product)
            transaction.savepoint()

    portal_setup.runAllImportStepsFromProfile('profile-Solgema.fullcalendar:default', purge_old=False)
    portal_quickinstaller.notifyInstalled('Solgema.fullcalendar')
    transaction.savepoint()

def uninstall( self ):
    out = StringIO()
    portal_setup = getToolByName(self, 'portal_setup')
    print >> out, "Removing Solgema.fullcalendar"
    portal_setup.runAllImportStepsFromProfile('profile-Solgema.fullcalendar:uninstall', purge_old=False)
    return out.getvalue()
