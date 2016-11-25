# -*- coding: utf-8 -*-
import zope.interface
from z3c.form import interfaces


class ITokenInputWidget(interfaces.ITextLinesWidget):
    """Text lines widget."""


class IEnhancedTextLinesWidget(interfaces.ITextLinesWidget):
    """Text lines widget."""


class ISimpleRichTextWidget(interfaces.ITextAreaWidget):
    """Simple RichText widget."""


class ILayer(zope.interface.Interface):
    """ A layer specific for collective.z3cform.widgets product."""
