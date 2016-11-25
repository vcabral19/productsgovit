from Products.CMFPlone.URLTool import URLTool
import re


orig = URLTool.isURLInPortal


def wrapped_in_portal(self, url, context=None):
    url = re.sub('^[\x00-\x20]+', '', url).strip()
    cmp_url = url.lower()
    if ('\\\\' in cmp_url or
            '<script' in cmp_url or
            '%3cscript' in cmp_url or
            'javascript:' in cmp_url or
            'javascript%3a' in cmp_url):
        return False

    try:
        return orig(self, url, context)
    except TypeError, e:
        if 'isURLInPortal() takes exactly 2 arguments' in e.args[0]:
            return orig(self, url)
        else:
            raise

wrapped_in_portal.__doc__ = orig.__doc__
URLTool.isURLInPortal = wrapped_in_portal
