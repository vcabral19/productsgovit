# -*- coding: utf-8 -*-
from httmock import all_requests
from httmock import HTTMock
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobImage
from Products.statusmessages.interfaces import IStatusMessage
from sc.embedder.content.embedder import Embedder
from sc.embedder.content.embedder import IEmbedder
from sc.embedder.testing import INTEGRATION_TESTING
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import json
import os
import unittest


PROVIDERS = {
    'youtube': 'http://www.youtube.com/watch?v=n-zxaVt6acg&feature=g-all-u',
    'vimeo': 'http://vimeo.com/17914974',
    'slideshare': 'http://www.slideshare.net/cgiorgi/secrets-of-a-good-pitch',
    'instagram': 'http://www.flickr.com/photos/jup3nep/6796214503/?f=hp',
}


@all_requests
def youtube_mock(url, request):
    """XXX: Avoid "HTTP Error 429: Too Many Requests" from YouTube when
    running on Travis CI.
    """
    if url.query == 'v=cwWzpkgwWuU':
        return dict(status_code=401)
    elif url.query == 'v=fpDw3s7XJKo':
        return dict(status_code=404)


class MultimediaTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']

        self.folder.invokeFactory('sc.embedder', 'multimedia')
        self.multimedia = self.folder['multimedia']
        self.multimedia.title = 'Multimedia'

        # Setup image
        path = os.path.dirname(__file__)
        data = open(os.path.join(path, 'image.jpg')).read()
        image = NamedBlobImage(data, 'image/jpeg', u'image.jpg')
        self.multimedia.image = image
        self.multimedia.reindexObject()

    def test_adding(self):
        self.assertTrue(IEmbedder.providedBy(self.multimedia))
        self.assertTrue(verifyClass(IEmbedder, Embedder))

    def test_interface(self):
        self.assertTrue(IEmbedder.providedBy(self.multimedia))
        self.assertTrue(verifyObject(IEmbedder, self.multimedia))

    def test_custom_player_size_addform(self):
        """ Check if the custom size applies to the embed code in the
            add form.
        """
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        dummy_data = {}
        dummy_data['embed_html'] = '<object width="512" height="296"><param ' + \
            'name="flashvars" value="ap=1"></param></object>'
        dummy_data['width'] = 300
        dummy_data['height'] = 200
        add_form = add_view.form_instance
        add_form.set_custom_embed_code(dummy_data)
        self.assertTrue('width="300"' in dummy_data['embed_html'])
        self.assertTrue('height="200"' in dummy_data['embed_html'])

    def test_custom_player_size_editform(self):
        """ Check if the custom size applies to the embed code in the
            edit form.
        """
        edit_view = self.multimedia.unrestrictedTraverse('edit')
        edit_form = edit_view.form_instance
        dummy_data = {}
        dummy_data['embed_html'] = '<object width="512" height="296"><param ' + \
            'name="flashvars" value="ap=1"></param></object>'
        dummy_data['width'] = 300
        dummy_data['height'] = 200
        edit_form.set_custom_embed_code(dummy_data)
        self.assertTrue('width="300"' in dummy_data['embed_html'])
        self.assertTrue('height="200"' in dummy_data['embed_html'])

    def test_player_position_class(self):
        """ Tests the return of the css class based on the position
            selected in the form.
        """
        view = self.multimedia.unrestrictedTraverse('view')

        # Classes
        self.multimedia.player_position = u'Top'
        pos_class = view.get_player_pos_class()
        self.assertEqual(pos_class, 'top_embedded')

        self.multimedia.player_position = u'Bottom'
        pos_class = view.get_player_pos_class()
        self.assertEqual(pos_class, 'bottom_embedded')

        self.multimedia.player_position = u'Left'
        pos_class = view.get_player_pos_class()
        self.assertEqual(pos_class, 'left_embedded')

        self.multimedia.player_position = u'Right'
        pos_class = view.get_player_pos_class()
        self.assertEqual(pos_class, 'right_embedded')

    def test_get_url_widget(self):
        from z3c.form.browser.text import TextWidget
        edit_view = self.multimedia.unrestrictedTraverse('edit')
        edit_form = edit_view.form_instance
        edit_form.update()
        url_wid = edit_view.get_url_widget()
        self.assertTrue(TextWidget, url_wid)
        self.assertEqual(url_wid.id, 'form-widgets-url')

    def test_get_load_action(self):
        from z3c.form.button import ButtonAction
        edit_view = self.multimedia.unrestrictedTraverse('edit')
        edit_form = edit_view.form_instance
        edit_form.update()
        load_act = edit_view.get_load_action()
        self.assertTrue(ButtonAction, load_act)
        self.assertEqual(load_act.id, 'form-buttons-load')

    def test_vimeo_oembed(self):
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        add_form = add_view.form_instance
        add_form.update()
        add_form.actions.update()

        add_form.widgets['url'].value = 'http://vimeo.com/17914974'
        action = add_form.actions['load']
        add_form.handleLoad(add_form, action)  # trigger load action

        self.assertEqual(
            add_form.widgets['IDublinCore.title'].value, u'The Backwater Gospel')
        self.assertNotEqual(
            add_form.widgets['IDublinCore.description'].value, u'')
        self.assertEqual(add_form.widgets['width'].value, u'1280')
        self.assertEqual(add_form.widgets['height'].value, u'720')
        self.assertIn(
            u'player.vimeo.com/video/17914974',
            add_form.widgets['embed_html'].value
        )

    def test_youtube_oembed(self):
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        add_form = add_view.form_instance
        add_form.update()
        add_form.actions.update()

        url = 'http://www.youtube.com/watch?v=d8bEU80gIzQ'
        add_form.widgets['url'].value = url
        action = add_form.actions['load']
        add_form.handleLoad(add_form, action)  # trigger load action

        self.assertEqual(
            add_form.widgets['IDublinCore.title'].value, u'Introducing Plone')
        self.assertEqual(
            add_form.widgets['IDublinCore.description'].value, u'')
        self.assertEqual(add_form.widgets['width'].value, u'459')
        self.assertEqual(add_form.widgets['height'].value, u'344')
        self.assertIn(
            u'www.youtube.com/embed/d8bEU80gIzQ',
            add_form.widgets['embed_html'].value
        )

    def test_slideshare_oembed(self):
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        add_form = add_view.form_instance
        add_form.update()
        add_form.actions.update()

        url = 'http://www.slideshare.net/baekholt/plone-4-and-5-plans-and-progress'

        add_form.widgets['url'].value = url
        action = add_form.actions['load']

        # We trigger the action of load
        add_form.handleLoad(add_form, action)

        # Search for chunks in the embed code
        self.assertIn(
            u'<iframe src="https://www.slideshare.net/slideshow/embed_code/key/SbXVOykqQSdtA"',
            add_form.widgets['embed_html'].value)
        self.assertIn(
            u'width="427" height="356"',  # XXX: why these values?
            add_form.widgets['embed_html'].value)
        self.assertIn(
            u'<a href="https://www.slideshare.net/baekholt/plone-4-and-5-plans-and-progress"',
            add_form.widgets['embed_html'].value)
        self.assertIn(
            u'title="Plone 4 and 5, plans and progress"',
            add_form.widgets['embed_html'].value)
        self.assertEqual(
            u'Plone 4 and 5, plans and progress',
            add_form.widgets['IDublinCore.title'].value)
        self.assertEqual(
            u'425', add_form.widgets['width'].value)
        self.assertEqual(
            u'355', add_form.widgets['height'].value)

    def test_soundcloud_oembed(self):
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        add_form = add_view.form_instance
        add_form.update()
        add_form.actions.update()

        # We check for Vimeo that has a more complete oembed implementation
        url = 'http://soundcloud.com/nuvru/semi-plone'
        add_form.widgets['url'].value = url
        action = add_form.actions['load']

        # We trigger the action of load
        add_form.handleLoad(add_form, action)

        # Discontinued direct comparison, as details may vary:

        """iframe = '<iframe width="100%" height="166" scrolling="no" ' + \
            'frameborder="no" src="https://w.soundcloud.com/' + \
            'player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks' + \
            '%2F4599497&show_artwork=true"></iframe>'
        """
        iframe_bits = ('<iframe', 'src=', 'api.soundcloud.com', 'tracks')

        self.assertEqual(
            u'Semi Plone by nuvru',
            add_form.widgets['IDublinCore.title'].value)
        self.assertEqual(
            u'Well... semi.',
            add_form.widgets['IDublinCore.description'].value)

        # self.assertEqual(
        #    iframe, add_form.widgets['embed_html'].value)
        value = add_form.widgets['embed_html'].value
        for bit in iframe_bits:
            self.assertTrue(bit in value)
        # XXX:  create similar or better semantical comparison of
        # iframe contents on the other tests - no API, neither
        # product has the obligation of returning the set space-count
        # inside generated HTML these tests are expecting, nor
        # are they broken if space count, or other html display
        # attrributes or order vary.

        # Sound cloud return percentage values
        self.assertEqual(
            u'100%', add_form.widgets['width'].value)
        # XXX: Does asserting a fixed-pixel count
        # not specified here makes sense?
        # Now this is breaking, we can't test for a value
        # that we don't control.
        # self.assertEqual(
        #    u'166', add_form.widgets['height'].value)

    def test_videojs(self):
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        add_form = add_view.form_instance
        add_form.update()
        add_form.actions.update()

        url = 'http://vjs.zencdn.net/v/oceans.webm'
        add_form.widgets['url'].value = url
        action = add_form.actions['load']

        # We trigger the action of load
        add_form.handleLoad(add_form, action)
        iframe = u'<iframe src="http://nohost/plone/test-folder/@@embedder_videojs?src=http%3A%2F%2Fvjs.zencdn.net%2Fv%2Foceans.webm&amp;type=video%2Fwebm" class="vjs-iframe" allowfullscreen>\n</iframe>'
        self.assertEqual(u'', add_form.widgets['IDublinCore.title'].value)
        # sometimes a trailing '\n' is added to the embed_html field
        self.assertIn(iframe, add_form.widgets['embed_html'].value)
        self.assertEqual(u'', add_form.widgets['width'].value)
        self.assertEqual(u'', add_form.widgets['height'].value)

        self.folder.invokeFactory('sc.embedder', 'ocean-clip')
        video = self.folder['ocean-clip']

        video.title = 'Oceans clip'
        video.width = '640'
        video.height = '264'
        video.embed_html = iframe

        rendered = json.loads(video.unrestrictedTraverse('@@tinymce-jsondetails')())
        expected = dict(
            description=u'',
            embed_html=u'%3Ciframe%20src%3D%22http%3A//nohost/plone/test-folder/%40%40embedder_videojs%3Fsrc%3Dhttp%253A%252F%252Fvjs.zencdn.net%252Fv%252Foceans.webm%26amp%3Btype%3Dvideo%252Fwebm%22%20class%3D%22vjs-iframe%22%20allowfullscreen%3E%0A%3C/iframe%3E',
            thumb_html=u'%3Ciframe%20src%3D%22http%3A//nohost/plone/test-folder/%40%40embedder_videojs%3Fsrc%3Dhttp%253A%252F%252Fvjs.zencdn.net%252Fv%252Foceans.webm%26amp%3Btype%3Dvideo%252Fwebm%22%20class%3D%22vjs-iframe%22%20allowfullscreen%20width%3D%22188%22%20height%3D%22141%22%3E%0A%3C/iframe%3E',
            title=u'Oceans clip'
        )
        self.assertEqual(rendered, expected)

    def test_facebook_manual(self):
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        add_form = add_view.form_instance
        add_form.update()
        embed_html = u"""<div id="fb-root"></div><script>(function(d, s, id) {  var js, fjs = d.getElementsByTagName(s)[0];  if (d.getElementById(id)) return;  js = d.createElement(s); js.id = id;  js.src = "//connect.facebook.net/pt_BR/sdk.js#xfbml=1&version=v2.3";  fjs.parentNode.insertBefore(js, fjs);}(document, 'script', 'facebook-jssdk'));</script><div class="fb-video" data-allowfullscreen="1" data-href="/cnnencuentro/videos/vb.195113273856041/1077980902235936/?type=3"><div class="fb-xfbml-parse-ignore"><blockquote cite="https://www.facebook.com/cnnencuentro/videos/1077980902235936/"><a href="https://www.facebook.com/cnnencuentro/videos/1077980902235936/"></a><p>¿Te parece complejo el conflicto de Siria? Dos creadores españoles explican el origen de la guerra civil en ese país en 10 minutos y en 15 mapas.</p>Posted by <a href="https://www.facebook.com/cnnencuentro/">CNN Encuentro</a> on Segunda, 12 de outubro de 2015</blockquote></div></div>"""
        data = {'embed_html': embed_html}
        add_form.set_custom_embed_code(data)

        # an additional div tag must be involving the original code
        self.assertTrue(
            data['embed_html'].startswith(u'<div><div id="fb-root"></div>'))
        self.assertTrue(
            data['embed_html'].endswith(u'</blockquote></div></div></div>'))

    def test_invalid_url(self):
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        add_form = add_view.form_instance
        add_form.update()
        add_form.actions.update()

        add_form.widgets['url'].value = (
            'www.flickr.com/photos/albionharrisonnaish/sets/72157642936095895/'
        )
        action = add_form.actions['load']
        add_form.handleLoad(add_form, action)  # trigger load action

        msg = IStatusMessage(self.request).show()
        self.assertEqual(len(msg), 1)
        expected = u'Invalid URL'
        self.assertEqual(msg[0].message, expected)

    def test_unauthorized_request(self):
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        add_form = add_view.form_instance
        add_form.update()
        add_form.actions.update()

        add_form.widgets['url'].value = 'https://www.youtube.com/watch?v=cwWzpkgwWuU'
        action = add_form.actions['load']

        with HTTMock(youtube_mock):
            add_form.handleLoad(add_form, action)  # trigger load action

        msg = IStatusMessage(self.request).show()
        self.assertEqual(len(msg), 1)
        expected = u'Unauthorized request'
        self.assertEqual(msg[0].message, expected)

    def test_url_not_found(self):
        add_view = self.folder.unrestrictedTraverse('++add++sc.embedder')
        add_form = add_view.form_instance
        add_form.update()
        add_form.actions.update()

        add_form.widgets['url'].value = 'https://www.youtube.com/watch?v=fpDw3s7XJKo'
        action = add_form.actions['load']

        with HTTMock(youtube_mock):
            add_form.handleLoad(add_form, action)  # trigger load action

        msg = IStatusMessage(self.request).show()
        self.assertEqual(len(msg), 1)
        expected = u'URL not found'
        self.assertEqual(msg[0].message, expected)

    def test_jsonimagefolderlisting(self):
        # Now we can get a listing of the images and check if our image is there.e/'})
        output = self.folder.restrictedTraverse('@@tinymce-jsonscembedderfolderlisting')(False, 'http://nohost/plone/test-folder')
        self.assertIn('"id": "multimedia"', output)

    def test_jsonimagesearch(self):
        # The images have a similar search method. Let's find our image.
        output = self.portal.restrictedTraverse('@@tinymce-jsonscembeddersearch')('Multimedia')
        self.assertIn('"id": "multimedia"', output)

    def test_image_thumb(self):
        ''' Test if traversing to image_thumb returns an image
        '''
        content = self.multimedia
        self.assertIsNotNone(content.restrictedTraverse('image_thumb')().read())

    def test_image_thumb_no_image(self):
        ''' Test if traversing to image_thumb returns None
        '''
        content = self.multimedia
        content.image = None
        self.assertIsNone(content.restrictedTraverse('image_thumb')())

        # set an empty image file
        content.image = NamedBlobImage('', 'image/jpeg', u'picture.jpg')
        self.assertIsNone(content.restrictedTraverse('image_thumb')())

    def test_image_tag(self):
        ''' Test if tag method works as expected
        '''
        content = self.multimedia
        expected = u'<img src="http://nohost/plone/test-folder/' + \
                   u'multimedia/@@images/'
        self.assertTrue(content.tag().startswith(expected))

        expected = u'height="90" width="120" class="tileImage" />'
        self.assertTrue(content.tag().endswith(expected))

    def test_image_tag_no_image(self):
        ''' Tag should return a default image if no picture available
        '''
        content = self.multimedia
        content.image = None
        expected = u''
        self.assertEqual(content.tag(), expected)

        # set an empty image file
        content.image = NamedBlobImage('', 'image/jpeg', u'picture.jpg')
        self.assertEqual(content.tag(), expected)
