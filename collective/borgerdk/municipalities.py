import os
import logging

from zope.schema.vocabulary import SimpleVocabulary
from collective.borgerdk import portal
from Products.CMFCore.utils import getToolByName

def Vocabulary(context):
    # get site to store the municipality list as a volatile attribute
    site = getToolByName(context, 'portal_url').getPortalObject()

    try:
        return site._v_municipality_vocabulary
    except AttributeError:
        client = portal.get_client()

        if client is not None:
            logging.info("Requesting municipality list...")
            data = client.service.GetMunicipalityList()
            logging.debug("Received %d items." % len(data))
            municipalities = data[0]
            logging.debug("Received %d municipalities." % len(municipalities))
            terms = [
                SimpleVocabulary.createTerm(
                    m.MunicipalityCode,
                    str(m.MunicipalityCode),
                    unicode(m.MunicipalityName).rsplit('Kommune', 1)[0].strip(),
                    ) for m in municipalities
                ]
        else:
            terms = []

        vocabulary = site._v_municipality_vocabulary = SimpleVocabulary(terms)

    return vocabulary
