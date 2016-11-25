from Products.ATContentTypes.interface import IATDocument
from Products.Archetypes.atapi import BooleanField, BooleanWidget
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.component import adapts, queryUtility
from zope.interface import implements, alsoProvides, noLongerProvides

from plone.contentratings.interfaces import IUnratable, \
    IRatingCategoryAssignment
from plone.contentratings.interfaces import _


class ReverseInterfaceField(ExtensionField, BooleanField):
    """Just a boolean field"""
    _properties = BooleanField._properties.copy()
    _properties.update({'interface': IUnratable})

    def get(self, instance, **kwargs):
        return not self._properties['interface'].providedBy(instance)

    def set(self, instance, value, **kwargs):
        iface = self._properties['interface']
        if not value or value == '0' or value == 'False':
            if not iface.providedBy(instance):
                alsoProvides(instance, iface)
        else:
            if iface.providedBy(instance):
                noLongerProvides(instance, iface)


class RatingRemover(object):
    """An adapter that adds the rating removal field"""
    adapts(IATDocument)
    implements(ISchemaExtender)

    fields = [ReverseInterfaceField(
        "allow_ratings",
        default=True,
        widget=BooleanWidget(
            label=_(u"Enable Ratings"),
            description= _('allow_ratings_help',
                           default=(u"Check this box to add ratings to this "
                                    u"item. Use the control panel to select "
                                    u"the ratings shown on each content type.")
                           )),
        schemata="settings"),
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """If the product is installed, return our custom field"""
        if queryUtility(IRatingCategoryAssignment) is not None:
            return self.fields
        else:
            return []
