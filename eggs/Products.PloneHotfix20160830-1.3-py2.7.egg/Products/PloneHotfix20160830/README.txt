Plone hotfix, 2016-08-30
========================

This hotfix fixes several security issues:

- An attacker could bypass Plone's security method to check if a url is a valid,
  safe url on the site which can lead to XSS attacks on certain pages.
- In multiple places, Plone blindly uses the `referer` header to redirect a user
  to the next page after a particular action. An attacker could utilize this to
  draw a user into a redirection attack.
- z3c.form will currently accept data from GET requests when the form is supposed
  to be POST. This allows a user to inject a potential XSS attack into a form,
  which when saved, will cause a XSS attack. Moreover, with certain widgets in Plone
  admin forms, the input is expected to be safe and can cause a reflexive XSS
  attack.
- Fixes XSS on user information page.
- Fixes XSS on multiple ZMI pages
- By using relative paths and guessing locations on a server Plone is installed
  on, an attacker can read data from a target server that the process running
  Plone has permission to read. The attacker needs administrator privileges on
  the Plone site to perform this attack.



This hotfix should be applied to the following versions of Plone:

* Plone 5.0.6 and any earlier 5.x version
* Plone 4.3.11 and any earlier 4.x version
* Any older version of Plone

The hotfix is officially supported by the Plone security team on the
following versions of Plone in accordance with the Plone
`version support policy`_: 4.0.10, 4.1.6, 4.2.7, 4.3.11 and 5.0.6.
However it has also received some testing on older versions of Plone.
The fixes included here will be incorporated into subsequent releases of Plone,
so Plone 4.3.12, 5.0.7 and greater should not require this hotfix.


Installation
============

Installation instructions can be found at
https://plone.org/security/hotfix/20160830


Applied patches
===============

Not all patches need to be applied in all Plone versions.

If you are using versions of plone.protect prior to 3, the "confirm" patch is
not necessary and will not successfully apply.  This is true for any
Plone 4 site that does not have plone4.csrffixes installed.

On default installs of Plone 4.x, the "user" patch will not successfully apply
and does not need to be patched. The patch is only applied when a version of
plone.app.users greater than 2 is installed.

On default installs of Plone 4.1.x or lower, the "resource" patch will
not successfully apply and does not need to be patched. The patch is
only applied when plone.resource is installed.

On default installs of Plone 4.0.x or lower, the "discussion" patch will
not successfully apply and does not need to be patched. The patch is
only applied when plone.app.discussion is installed.

On default installs of Plone 3 or lower, the "plonerootlogin" patch
will not successfully apply and does not need to be patched. The patch
is only applied on Plone 4 and higher.

On default installs of Plone 3 or lower, the "z3c_form" patch
will not successfully apply and does not need to be patched. The patch
is only applied when z3c.form is installed.


Redirection to external sites
=============================

For any controller page template or script that uses the
``redirect_to`` action, the url is now checked.  If the url is not in
the current portal and the domain is not in the
"allow_external_login_sites" property, then Plone refuses to redirect
to this, and instead redirects to the current page.

One example where this might affect you, is if you use an external
site to login (for example openid, Facebook, Google), or when the
Plone Site itself is setup as openid provider for other sites.  In
this or similar cases, you need to update the
"allow_external_login_sites" property.

- On Plone 5 this can done in the Configuration Registry:
  ``/portal_registry/edit/plone.allow_external_login_sites``

- On Plone 4 and lower this can only be done in the Zope Management interface:
  ``portal_properties/site_properties/manage_propertiesForm``.

If you have own controller page templates or scripts and want to allow
redirection to external sites without editing this property, you can
edit the ``.metadata`` file of this template or script and change
``redirect_to`` into ``external_redirect_to``.  This allows both
internal and external redirects.  This action has been added in this
hotfix, and will be added to future versions of
``Products.CMFFormController``.


z3c.form and prefilling data
============================

With this hotfix, we only use data from the request when the request
method matches the form method.  By default all forms are meant for
POST requests, and in those we no longer allow prefilling data from a
GET request.  The same is true the other way around, we don't fill in
data from POST requests in forms that expect a GET request, but that
likely does not happen often.

If you have a form where this protection is not wanted, you can add an
attribute ``allow_prefill_from_GET_request`` on the form and set it to
a True value.  If you want, you can import this attribute name from
``Products.PloneHotfix20160830.z3c_form.ALLOW_PREFILL``.  This
attribute will likely be ported to the z3c.form package.

The attribute was introduced in version 1.3 of the hotfix.


Q&A
===

Q: How can I confirm that the hotfix is installed correctly and my site is protected?
  A: On startup, the hotfix will log a number of messages to the Zope event log
  that look like this::

      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied resource patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied confirm patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied z3c_form patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied in_portal patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied plonerootlogin patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied redirects patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied redirect_folderfactories patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied redirect_qi patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied redirectto patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied discussion patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied user patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Applied zmi patch
      2016-08-30 08:46:09 INFO Products.PloneHotfix20160830 Hotfix installed

  The exact number of patches applied, will differ depending on what packages you are using.
  If a patch is attempted but fails, it will be logged as a warning that says
  "Could not apply". This may indicate that you have a non-standard Plone
  installation.

Q: How can I report problems installing the patch?
  A: Contact the Plone security team at security@plone.org, or visit the
  #plone channel on freenode IRC.

Q: How can I report other potential security vulnerabilities?
  A: Please email the security team at security@plone.org rather than discussing
  potential security issues publicly.

.. _`version support policy`: http://plone.org/support/version-support-policy
