# -*- coding: utf-8 -*-
from brasil.gov.tiles.testing import INTEGRATION_TESTING
from brasil.gov.tiles.tiles.mediacarousel import IMediaCarouselTile
from brasil.gov.tiles.tiles.mediacarousel import MediaCarouselTile
from collective.cover.tests.base import TestTileMixin
from mock import Mock
from plone.app.imaging.interfaces import IImageScale
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

import unittest


class MediaCarouselTileTestCase(TestTileMixin, unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        super(MediaCarouselTileTestCase, self).setUp()
        self.tile = MediaCarouselTile(self.cover, self.request)
        self.tile.__name__ = u'mediacarousel'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IMediaCarouselTile
        self.klass = MediaCarouselTile
        super(MediaCarouselTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_droppable)
        self.assertTrue(self.tile.is_editable)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['Collection', 'Folder'])

    def test_folder_tile_render(self):
        obj = self.portal['my-folder']
        self.tile.populate_with_object(obj)

        rendered = self.tile()
        msg = u'Drag a folder or collection to populate the tile.'
        self.assertIn(msg, rendered)

    def test_delete_folder(self):
        obj = self.portal['my-folder']
        self.tile.populate_with_object(obj)
        self.tile.populate_with_object(obj)

        rendered = self.tile()
        msg = u'Drag a folder or collection to populate the tile.'
        self.assertIn(msg, rendered)

        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Editor', 'Reviewer'])
        login(self.portal, TEST_USER_NAME)
        self.portal.manage_delObjects(['my-folder'])

        rendered = self.tile()
        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, rendered)

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertIn(msg, self.tile())

    def test_collection_tile_render(self):
        obj = self.portal['my-collection']
        self.tile.populate_with_object(obj)

        rendered = self.tile()
        msg = u'Drag a folder or collection to populate the tile.'
        self.assertIn(msg, rendered)

    def test_delete_collection(self):
        obj = self.portal['my-collection']
        self.tile.populate_with_object(obj)
        self.tile.populate_with_object(obj)

        rendered = self.tile()
        msg = u'Drag a folder or collection to populate the tile.'
        self.assertIn(msg, rendered)

        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Editor', 'Reviewer'])
        login(self.portal, TEST_USER_NAME)
        self.portal.manage_delObjects(['my-collection'])

        rendered = self.tile()
        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, rendered)

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertIn(msg, self.tile())

    def test_thumbnail(self):
        # as a File does not have an image field, we should have no thumbnail
        obj = self.portal['my-file']
        self.assertFalse(self.tile.thumbnail(obj))

        # as an Image does have an image field, we should have a thumbnail
        obj = self.portal['my-image']
        thumbnail = self.tile.thumbnail(obj)
        self.assertTrue(thumbnail)
        # the thumbnail is an ImageScale
        self.assertTrue(IImageScale.providedBy(thumbnail))

        # turn visibility off, we should have no thumbnail
        # XXX: refactor; we need a method to easily change field visibility
        tile_conf = self.tile.get_tile_configuration()
        tile_conf['image']['visibility'] = u'off'
        self.tile.set_tile_configuration(tile_conf)

        self.assertFalse(self.tile._field_is_visible('image'))
        self.assertTrue(self.tile.thumbnail(obj))

        # TODO: test against Dexterity-based content types
