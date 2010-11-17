import logging

from suds import client as suds

from zope.component import getUtility
from zope.component import ComponentLookupError
from plone.registry.interfaces import IRegistry
from collective.borgerdk.interfaces import IBorgerPortalSettings

def get_client():
    registry = getUtility(IRegistry)

    try:
        client = registry._v_soap_client
    except AttributeError:
        try:
            settings = registry.forInterface(IBorgerPortalSettings)
        except ComponentLookupError:
            return

        # only log critical warnings from SUDS client software
        logging.getLogger('suds.client').setLevel(logging.CRITICAL)

        logging.info("Connecting to SOAP service: %s..." % settings.url)
        client = registry._v_soap_client = suds.Client(settings.url)

    return client
