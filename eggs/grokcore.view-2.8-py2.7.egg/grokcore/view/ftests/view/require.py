"""
Viewing a protected view with insufficient privileges will yield
Unauthorized:

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.open("http://localhost/@@painting")
  Traceback (most recent call last):
  HTTPError: HTTP Error 401: Unauthorized

When we log in (e.g. as a manager), we can access the view just fine:

  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/@@painting")
  >>> print browser.contents
  What a beautiful painting.

A view protected with 'zope.Public' is always accessible:

  >>> browser = Browser()
  >>> browser.open("http://localhost/@@publicnudity")
  >>> print browser.contents
  Everybody can see this.
"""

import grokcore.view as grok
import zope.interface


class ViewPainting(grok.Permission):
    grok.name('cave.ViewPainting')


class Painting(grok.View):
    grok.context(zope.interface.Interface)
    grok.require(ViewPainting)

    def render(self):
        return 'What a beautiful painting.'


class PublicNudity(grok.View):
    grok.context(zope.interface.Interface)
    grok.require(grok.Public)

    def render(self):
        return 'Everybody can see this.'
