import logging

logger = logging.getLogger('Products.PloneHotfix20160830')

# General hotfixes for all.
hotfixes = [
    'resource',
    'confirm',
    'z3c_form',
    'in_portal',
    'plonerootlogin',
    'redirects',
    'redirect_folderfactories',
    'redirect_qi',
    'redirectto',
    'discussion',
    'user',
    'zmi'
]


# Apply the fixes
for hotfix in hotfixes:
    try:
        __import__('Products.PloneHotfix20160830.%s' % hotfix)
        logger.info('Applied %s patch' % hotfix)
    except:
        logger.warn('Could not apply %s' % hotfix)
if not hotfixes:
    logger.info('No hotfixes were needed.')
else:
    logger.info('Hotfix installed')
