"""
Make sure that only interfaces extending IBrowserRequest can be
registered as a skin:

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
    ...
  GrokError: The grok.skin() directive is used on interface
  'grokcore.view.tests.skin.notonlayer.NotALayer'. However,
  'grokcore.view.tests.skin.notonlayer.NotALayer' does not extend
  IBrowserRequest which is required for interfaces that are used as
  layers and are to be registered as a skin.
"""
import grokcore.view as grok
from zope.interface import Interface

class NotALayer(Interface):
    grok.skin('not a layer')
