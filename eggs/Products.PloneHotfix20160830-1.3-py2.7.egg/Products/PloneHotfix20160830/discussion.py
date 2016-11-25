# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.discussion.browser.moderation import DeleteComment
from plone.app.discussion.browser.moderation import PublishComment
from plone.app.discussion.interfaces import _
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.statusmessages.interfaces import IStatusMessage


def DeleteComment__call__(self):
    comment = aq_inner(self.context)
    conversation = aq_parent(comment)
    content_object = aq_parent(conversation)
    # conditional security
    # base ZCML condition zope2.deleteObject allows 'delete own object'
    # modify this for 'delete_own_comment_allowed' controlpanel setting
    # can_delete was introduced in 2.3.3.
    if not base_hasattr(self, 'can_delete') or self.can_delete(comment):
        del conversation[comment.id]
        content_object.reindexObject()
        IStatusMessage(self.context.REQUEST).addStatusMessage(
            _('Comment deleted.'),
            type='info')
    came_from = self.context.REQUEST.HTTP_REFERER
    # if the referrer already has a came_from in it, don't redirect back
    if (len(came_from) == 0 or 'came_from=' in came_from
            or not getToolByName(
                content_object, 'portal_url').isURLInPortal(came_from)):
        came_from = content_object.absolute_url()
    return self.context.REQUEST.RESPONSE.redirect(came_from)


def PublishComment__call__(self):
    comment = aq_inner(self.context)
    content_object = aq_parent(aq_parent(comment))
    workflowTool = getToolByName(comment, 'portal_workflow', None)
    workflow_action = self.request.form.get('workflow_action', 'publish')
    workflowTool.doActionFor(comment, workflow_action)
    comment.reindexObject()
    content_object.reindexObject(idxs=['total_comments'])
    IStatusMessage(self.context.REQUEST).addStatusMessage(
        _('Comment approved.'),
        type='info')
    came_from = self.context.REQUEST.HTTP_REFERER
    # if the referrer already has a came_from in it, don't redirect back
    if (len(came_from) == 0 or 'came_from=' in came_from
            or not getToolByName(
                content_object, 'portal_url').isURLInPortal(came_from)):
        came_from = content_object.absolute_url()
    return self.context.REQUEST.RESPONSE.redirect(came_from)


DeleteComment.__call__ = DeleteComment__call__
PublishComment.__call__ = PublishComment__call__
