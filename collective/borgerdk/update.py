import suds
import logging

from zope.component import getUtility
from zExceptions import Unauthorized

from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from collective.borgerdk.content import get_article_metadata
from collective.borgerdk.content import update_content
from collective.borgerdk.portal import get_client
from collective.borgerdk import security
from collective.borgerdk.interfaces import IBorgerPortalSettings
from collective.borgerdk import MessageFactory as _
from plone.registry.interfaces import IRegistry


class UpdateView(BrowserView):
    def __call__(self, token):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IBorgerPortalSettings)

        if token != settings.synchronization_token:
            raise Unauthorized("Token mismatch or missing token.")

        client = get_client()

        # get all synchronized documents
        brains = self.context.portal_catalog(
            portal_type="Document",
            review_state="synchronized"
            )

        for brain in brains:
            document = brain.getObject()
            metadata = get_article_metadata(document)

            # retrieve article
            try:
                article = client.service.GetArticleByID(
                    metadata.id,
                    metadata.municipality
                    )
            except suds.WebFault, exc:
                logging.warn(exc)
                title = document.Title().decode('utf-8')
                IStatusMessage(self.request).addStatusMessage(
                    _(u"Fejl ved opdatering af artikel: ${title}.",
                      mapping={'title': title}),
                    type="warning"
                    )

                continue

            # as unrestricted user ...
            old = security.loginAsUnrestrictedUser()
            try:
                # update document content
                update_content(document, article)
            finally:
                security.loginAsUser(old)

        return len(brains)
