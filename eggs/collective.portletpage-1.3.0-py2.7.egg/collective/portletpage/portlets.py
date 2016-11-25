from collective.portletpage.interfaces import IPortletPageColumn
from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletContext
from plone.portlets.retriever import PortletRetriever
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import Interface

from plone.portlets.interfaces import IPortletAssignmentSettings


class PortletPageRetriever(PortletRetriever):
    """Fetch portlets to display in a portlet page column.
    """
    adapts(Interface, IPortletPageColumn)

    def getPortlets(self):
        """Work out which portlets to display, returning a list of dicts
        describing assignments to render.
        """
        manager = self.storage.__name__

        pcontext = IPortletContext(self.context, None)
        if pcontext is None:
            return []

        assignable = ILocalPortletAssignable(self.context, None)
        if assignable is None:
            return []

        annotations = IAnnotations(assignable, None)
        if annotations is None:
            return []

        local = annotations.get(CONTEXT_ASSIGNMENT_KEY, None)
        if local is None:
            return []

        localManager = local.get(manager, None)
        if localManager is None:
            return []

        assignments = []
        for assignment in localManager.values():
	    try:
		settings = IPortletAssignmentSettings(assignment)
	    except TypeError:
		# Portlet does not exist any longer
		continue
	    if not settings.get('visible', True):
		continue
            assignments.append(assignment)

        return [{'category': CONTEXT_CATEGORY,
                 'key': pcontext.uid,
                 'name': a.__name__,
                 'assignment': a} for a in assignments]
