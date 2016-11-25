try:
    from plone.app.users.browser.userdatapanel import UserDataPanel
except ImportError:
    from plone.app.users.browser.personalpreferences import UserDataPanel
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

import cgi


def description(self):
    userid = self.request.form.get('userid')
    mt = getToolByName(self.context, 'portal_membership')
    if userid and (userid != mt.getAuthenticatedMember().getId()):
        # editing someone else's profile
        return _(
            u'description_personal_information_form_otheruser',
            default='Change personal information for $name',
            mapping={'name': cgi.escape(userid)}
        )
    else:
        # editing my own profile
        return _(
            u'description_personal_information_form',
            default='Change your personal information'
        )

UserDataPanel.description = property(description)
