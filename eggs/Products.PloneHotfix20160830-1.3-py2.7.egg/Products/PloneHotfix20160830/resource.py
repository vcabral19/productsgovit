from plone.resource.directory import FilesystemResourceDirectory
import os
from zExceptions import Forbidden


def _resolveSubpath(self, path):
    parts = path.split('/')
    filepath = os.path.abspath(os.path.join(self.directory, *parts))
    if not filepath.startswith(self.directory):
        raise Forbidden('Invalid path resource')

    return filepath


FilesystemResourceDirectory._resolveSubpath = _resolveSubpath
