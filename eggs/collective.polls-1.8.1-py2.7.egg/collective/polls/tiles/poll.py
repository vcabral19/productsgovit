# -*- coding: utf-8 -*-
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.polls import MessageFactory as _
from collective.polls.browser import PollsViewMixin
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema import TextLine


class IPollTile(IPersistentCoverTile):

    """A tile that shows a poll."""

    uuid = TextLine(
        title=_(u'Poll uuid'),
        readonly=True,
    )


class PollTile(PollsViewMixin, PersistentCoverTile):

    """A tile that shows a poll."""

    index = ViewPageTemplateFile('poll.pt')

    is_configurable = False

    def results(self):
        uuid = self.data.get('uuid', None)
        if uuid is not None:
            obj = uuidToObject(uuid)
            return obj

    def poll(self):
        utility = self.utility
        uid = uuid = self.data.get('uuid', None)
        poll = None
        if uuid is not None:
            poll = utility.poll_by_uid(uid)
        if not poll:
            # if we have no open poll, try closed ones
            results = utility.recent_polls(show_all=True,
                                           limit=1,
                                           review_state='closed')
            poll = results and results[0].getObject() or None
        return poll

    def populate_with_object(self, obj):
        super(PollTile, self).populate_with_object(obj)
        uuid = IUUID(obj, None)
        data_mgr = ITileDataManager(self)
        data_mgr.set({'uuid': uuid})

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        return ['collective.polls.poll']

    def has_data(self):
        uuid = self.data.get('uuid', None)
        return uuid is not None
