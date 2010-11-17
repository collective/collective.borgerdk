import random

from zope.component import getUtility
from zope.component import queryAdapter
from plone.registry.record import Record
from plone.registry.interfaces import IRegistry
from plone.registry.interfaces import IPersistentField
from collective.borgerdk.interfaces import IBorgerPortalSettings

def setupWorkflow(context):
    site = context.getSite()

    # set new chain on documents
    site.portal_workflow.setChainForPortalTypes(
        ['Document'], ['synchronizable_document_workflow']
        )

def setupSynchronizationToken(context):
    # create random (string) token
    token = u"%016x" % random.getrandbits(128)

    # get persistent control panel settings field
    field = IBorgerPortalSettings['synchronization_token']
    persistent_field = queryAdapter(field, IPersistentField)

    # determine registry key
    key = IBorgerPortalSettings.__identifier__ + "." + field.__name__

    # registry is a utility component
    registry = getUtility(IRegistry)

    # set token in registry -- we need to work directly with the
    # `records` object because the field is read-only
    registry.records[key] = Record(
        persistent_field,
        token,
        interface=IBorgerPortalSettings,
        fieldName=field.__name__
        )
