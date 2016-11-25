# -*- coding: utf-8 -*-
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes import atapi
from collective.portletpage.config import PROJECTNAME
from collective.portletpage.interfaces import IPortletPage
from zope.interface import implements


PortletPageSchema = document.ATDocumentSchema.copy()
PortletPageSchema['title'].storage = atapi.AnnotationStorage()
PortletPageSchema['title'].required = False
PortletPageSchema['description'].storage = atapi.AnnotationStorage()
PortletPageSchema['text'].storage = atapi.AnnotationStorage()
finalizeATCTSchema(PortletPageSchema)


class PortletPage(document.ATDocument):
    """A page with some body text and a list of portlets.
    """
    implements(IPortletPage)
    portal_type = "Portlet Page"

    _at_rename_after_creation = True
    schema = PortletPageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')

atapi.registerType(PortletPage, PROJECTNAME)
