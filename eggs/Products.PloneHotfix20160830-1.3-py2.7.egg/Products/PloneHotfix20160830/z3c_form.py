from urlparse import urlparse
from z3c.form import widget


# Attribute name to allow prefilling a widget with a value from a GET request.
# Usually all forms are only for POST, and we disallow filling it with GET
# data.  This works the way around too: allow prefilling from a POST request
# when the form only handles GET.  But that is unlikely.
ALLOW_PREFILL = 'allow_prefill_from_GET_request'


def _wrap_update(update):
    def _wrapped(self):
        # If we are not already ignoring the request, check the referer.
        if not self.ignoreRequest and hasattr(self.request, 'environ'):
            env = self.request.environ
            referrer = env.get('HTTP_REFERER', env.get('HTTP_REFERRER'))
            if referrer:
                req_url_parsed = urlparse(self.request.URL)
                referrer_parsed = urlparse(referrer)
                if hasattr(req_url_parsed, 'netloc'):
                    request_netloc = req_url_parsed.netloc
                    referrer_netloc = referrer_parsed.netloc
                else:
                    # On Python 2.4 (Plone 3) there is no netloc...
                    request_netloc = req_url_parsed[1]
                    referrer_netloc = referrer_parsed[1]
                if request_netloc != referrer_netloc:
                    # We do not trust data from outside referrers.
                    self.ignoreRequest = True
        # If we are not already ignoring the request, check the request method.
        if not self.ignoreRequest and hasattr(self.form, 'method'):
            if self.request.REQUEST_METHOD.lower() != self.form.method.lower():
                # This is an unexpected request method.
                # For special cases we allow a form to bail out.
                if not getattr(self.form, ALLOW_PREFILL, False):
                    self.ignoreRequest = True
        return update(self)
    return _wrapped


widget.Widget.update = _wrap_update(widget.Widget.update)
