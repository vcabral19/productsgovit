# -*- coding: utf-8 -*-
from copy import deepcopy
import logging

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from diazo import rules
from diazo import cssrules
from diazo import compiler
from lxml import etree
from lxml import html
from diazo import utils
from plone.memoize import ram
from plone.memoize.volatile import DontCache
from plone.registry.interfaces import IRegistry
from zExceptions import NotFound
from z3c.form.interfaces import IFieldWidget
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.security.interfaces import IPermission
from zope.site.hooks import getSite
import Globals

from plone.app.blocks.interfaces import DEFAULT_SITE_LAYOUT_REGISTRY_KEY
from plone.app.blocks.interfaces import DEFAULT_AJAX_LAYOUT_REGISTRY_KEY
from plone.app.blocks.layoutbehavior import ILayoutAware
from plone.subrequest import subrequest


headXPath = etree.XPath("/html/head")
layoutAttrib = 'data-layout'
layoutXPath = etree.XPath("/html/@" + layoutAttrib)
gridAttrib = 'data-gridsystem'
gridXPath = etree.XPath("/html/@" + gridAttrib)
tileAttrib = 'data-tile'
tileRulesAttrib = 'data-rules'
headTileXPath = etree.XPath("/html/head//*[@" + tileAttrib + "]")
bodyTileXPath = etree.XPath("/html/body//*[@" + tileAttrib + "]")
panelXPath = etree.XPath("//*[@data-panel]")
gridDataAttrib = 'data-grid'
gridDataXPath = etree.XPath("//*[@" + gridDataAttrib + "]")
logger = logging.getLogger('plone.app.blocks')


def extractCharset(response, default='utf-8'):
    """Get the charset of the given response
    """

    charset = default
    if 'content-type' in response.headers:
        for item in response.headers['content-type'].split(';'):
            if item.strip().startswith('charset'):
                charset = item.split('=')[1].strip()
                break
    return charset


def resolve(url):
    """Resolve the given URL to an lxml tree.
    """

    resolved = resolveResource(url)
    if not resolved.strip():
        return None
    try:
        if isinstance(resolved, unicode):
            html_parser = html.HTMLParser(encoding='utf-8')
            return html.fromstring(resolved.encode('utf-8'),
                                   parser=html_parser).getroottree()
        else:
            return html.fromstring(resolved).getroottree()
    except etree.XMLSyntaxError as e:
        logger.error('%s: %s' % (repr(e), url))
        return None


def resolveResource(url):
    """Resolve the given URL to a unicode string. If the URL is an absolute
    path, it will be made relative to the Plone site root.
    """
    if url.startswith('/'):
        site = getSite()
        url = '/'.join(site.getPhysicalPath()) + url

    response = subrequest(url)
    if response.status == 404:
        raise NotFound(url)

    resolved = response.getBody()

    if isinstance(resolved, str):
        charset = extractCharset(response)
        resolved = resolved.decode(charset)

    if response.status in (301, 302):
        site = getSite()
        location = response.headers.get('location') or ''
        if location.startswith(site.absolute_url()):
            return resolveResource(location[len(site.absolute_url()):])

    elif response.status != 200:
        raise RuntimeError(resolved)

    return resolved


def xpath1(xpath, node, strict=True):
    """Return a single node matched by the given etree.XPath object.
    """

    if isinstance(xpath, basestring):
        xpath = etree.XPath(xpath)

    result = xpath(node)
    if len(result) == 1:
        return result[0]
    else:
        if (len(result) > 1 and strict) or len(result) == 0:
            return None
        else:
            return result


def append_text(element, text):
    if text:
        element.text = (element.text or '') + text


def append_tail(element, text):
    if text:
        element.tail = (element.tail or '') + text


def replace_with_children(element, wrapper):
    """element.replace also replaces the tail and forgets the wrapper.text
    """
    # XXX needs tests
    parent = element.getparent()
    index = parent.index(element)
    if index == 0:
        previous = None
    else:
        previous = parent[index - 1]
    if wrapper is None:
        children = []
    else:
        if index == 0:
            append_text(parent, wrapper.text)
        else:
            append_tail(previous, wrapper.text)
        children = wrapper.getchildren()
    parent.remove(element)
    if not children:
        if index == 0:
            append_text(parent, element.tail)
        else:
            append_tail(previous, element.tail)
    else:
        append_tail(children[-1], element.tail)
        children.reverse()
        for child in children:
            parent.insert(index, child)


def replace_content(element, wrapper):
    """Similar to above but keeps parent tag
    """
    del element[:]
    if wrapper is not None:
        element.text = wrapper.text
        element.extend(wrapper.getchildren())


def getDefaultSiteLayout(context):
    """Get the path to the site layout to use by default for the given content
    object
    """

    # Note: the sectionSiteLayout on context is for pages *under* context, not
    # necessarily context itself

    parent = aq_parent(aq_inner(context))
    while parent is not None:
        layoutAware = ILayoutAware(parent, None)
        if layoutAware is not None:
            if getattr(layoutAware, 'sectionSiteLayout', None):
                return layoutAware.sectionSiteLayout
        parent = aq_parent(aq_inner(parent))

    registry = queryUtility(IRegistry)
    if registry is None:
        return None

    return registry.get(DEFAULT_SITE_LAYOUT_REGISTRY_KEY)


def getDefaultAjaxLayout(context):
    """Get the path to the ajax site layout to use by default for the given
    content object
    """

    registry = queryUtility(IRegistry)
    if registry is not None:
        return registry.get(DEFAULT_AJAX_LAYOUT_REGISTRY_KEY)
    else:
        return getLayoutAwareSiteLayout(context)


def getLayoutAwareSiteLayout(context):
    """Get the path to the site layout for a page. This is generally only
    appropriate for the view of this page. For a generic template or view, use
    getDefaultSiteLayout(context) instead.
    """

    layoutAware = ILayoutAware(context, None)
    if layoutAware is not None:
        if getattr(layoutAware, 'pageSiteLayout', None):
            return layoutAware.pageSiteLayout

    return getDefaultSiteLayout(context)


class PermissionChecker(object):

    def __init__(self, permissions, context):
        self.permissions = permissions
        self.context = context
        self.sm = getSecurityManager()
        self.cache = {}

    def allowed(self, field_name):
        permission_name = self.permissions.get(field_name, None)
        if permission_name is not None:
            if permission_name not in self.cache:
                permission = queryUtility(IPermission, name=permission_name)
                if permission is None:
                    self.cache[permission_name] = True
                else:
                    self.cache[permission_name] = bool(
                        self.sm.checkPermission(permission.title,
                                                self.context),
                    )
        return self.cache.get(permission_name, True)


def _getWidgetName(field, widgets, request):
    if field.__name__ in widgets:
        factory = widgets[field.__name__]
    else:
        factory = getMultiAdapter((field, request), IFieldWidget)
    if isinstance(factory, basestring):
        return factory
    if not isinstance(factory, type):
        factory = factory.__class__
    return '%s.%s' % (factory.__module__, factory.__name__)


def isVisible(name, omitted):
    value = omitted.get(name, False)
    if isinstance(value, basestring):
        return value == 'false'
    else:
        return not bool(value)


def add_theme(rules_doc, theme_doc, absolute_prefix=None):
    if absolute_prefix is None:
        absolute_prefix = ''
    root = rules_doc.getroot()
    element = root.makeelement(
        rules.fullname(rules.namespaces['diazo'], 'theme'))
    root.append(element)
    rules.expand_theme(element, theme_doc, absolute_prefix)
    return rules_doc


def process_rules(rules_doc, theme=None, trace=None, css=True,
                  absolute_prefix=None, includemode=None,
                  update=True, stop=None):
    if trace:
        trace = '1'
    else:
        trace = '0'
    if stop == 0:
        return rules_doc
    if stop == 1:
        return rules_doc
    rules_doc = rules.add_identifiers(rules_doc)
    if stop == 2 or stop == 'add_identifiers':
        return rules_doc
    if update:
        rules_doc = rules.update_namespace(rules_doc)
    if stop == 3:
        return rules_doc
    if css:
        rules_doc = cssrules.convert_css_selectors(rules_doc)
    if stop == 4:
        return rules_doc
    rules_doc = rules.fixup_theme_comment_selectors(rules_doc)
    if stop == 5:
        return rules_doc
    if theme is not None:
        rules_doc = add_theme(rules_doc, theme, absolute_prefix)
    if stop == 6:
        return rules_doc
    if includemode is None:
        includemode = 'document'
    includemode = "'%s'" % includemode
    rules_doc = rules.normalize_rules(rules_doc, includemode=includemode)
    if stop == 7:
        return rules_doc
    rules_doc = rules.apply_conditions(rules_doc)
    if stop == 8:
        return rules_doc
    rules_doc = rules.merge_conditions(rules_doc)
    if stop == 9:
        return rules_doc
    rules_doc = rules.fixup_themes(rules_doc)
    if stop == 10:
        return rules_doc
    rules_doc = rules.annotate_themes(rules_doc)
    if stop == 11:
        return rules_doc
    rules_doc = rules.annotate_rules(rules_doc)
    if stop == 12:
        return rules_doc
    rules_doc = rules.apply_rules(rules_doc, trace=trace)
    return rules_doc


def compile_theme(rules_doc, theme_doc=None, css=True,
                  absolute_prefix=None, update=True, trace=False,
                  includemode=None, parser=None, compiler_parser=None):
    rules_doc = process_rules(
        rules_doc=rules_doc,
        theme=theme_doc,
        css=css,
        absolute_prefix=absolute_prefix,
        update=update,
        trace=trace,
        includemode=includemode,
    )

    # Build a document with all the <xsl:param /> values to set the defaults
    # for every value passed in as xsl_params
    known_params = compiler.build_xsl_params_document({})

    # Create a pseudo resolver for this
    known_params_url = 'file:///__diazo_known_params__'
    emit_stylesheet_resolver = utils.CustomResolver({
        known_params_url: etree.tostring(known_params)})
    emit_stylesheet_parser = etree.XMLParser()
    emit_stylesheet_parser.resolvers.add(emit_stylesheet_resolver)

    # Run the final stage compiler
    emit_stylesheet = utils.pkg_xsl(
        'emit-stylesheet.xsl', parser=emit_stylesheet_parser)
    compiled_doc = emit_stylesheet(rules_doc)
    compiled_doc = compiler.set_parser(
        etree.tostring(compiled_doc), parser, compiler_parser)

    return compiled_doc


def cacheKey(func, rules_url, theme_node):
    if Globals.DevelopmentMode:
        raise DontCache()
    return ':'.join([rules_url, html.tostring(theme_node)])


@ram.cache(cacheKey)
def resolve_transform(rules_url, theme_node):
    rules_doc = resolveResource(rules_url)  # may raise NotFound
    rules_doc = etree.ElementTree(etree.fromstring(rules_doc))
    compiled = compile_theme(rules_doc,
                             etree.ElementTree(deepcopy(theme_node)))
    transform = etree.XSLT(compiled)
    return transform
