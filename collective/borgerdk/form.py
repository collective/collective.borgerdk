import suds
import urllib
import logging
import urlparse

import BeautifulSoup as bsoup

from zope import interface
from zope import schema
from zope.interface import Invalid
from zope.component import queryUtility
from zExceptions import BadRequest

from z3c.form import button
from z3c.form import field
from z3c.form import form

from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.memoize.volatile import cache
from plone.app.z3cform.layout import wrap_form
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from collective.borgerdk import MessageFactory as _
from collective.borgerdk import portal
from collective.borgerdk.content import get_article_metadata
from collective.borgerdk.content import update_content

NOT_AN_ARTICLE = _(
    u"No article information found at location. " \
    u"Make sure the link is for an article and " \
    u"not a news item or similar."
    )
NO_PERMANENT_LOCATION = _(u"Unable to find permanent link at location.")
CANT_DOWNLOAD = _(u"Unable to download page.")
CANT_PARSE = _(u"Unable to parse document.")
CANT_ADD = _(u"Unable to add article.")
SYSTEM_ERROR = _(u"System error.")
ALREADY_EXISTS = _(u"Article already exists.")
ADDED = _(u"Article added.")


def status(request, message, type='info'):
    IStatusMessage(request).addStatusMessage(
        message, type=type)


def check_url(url):
    if not urlparse.urlparse(url)[1].endswith('borger.dk'):
        raise Invalid(_(u"Must be a URL from borger.dk."))

    return True


class AlreadyExists(Exception):
    """Item was attempted added, but exists already."""

    def __init__(self, name):
        self.name = name


class ILocalization(interface.Interface):
    municipality = schema.Choice(
        title=_(u"Municipality"),
        description=_(u"Select a municipality to receive localized content."),
        required=False,
        vocabulary="vocabulary.Municipalities"
        )


class ISynchronizeForm(ILocalization):
    url = schema.TextLine(
        title=_(u"Article URL"),
        description=_(u"Paste the article link into this field."),
        required=True,
        constraint=check_url,
        )

class SynchronizeForm(form.Form):
    """Adds a new synchronized document to the site."""

    fields = field.Fields(ISynchronizeForm)
    ignoreContext = True
    label = _(u"Add a synchronized article")
    description = _(
        u"Use this form to show documents from the portal " \
        u"on your site. Content is automatically synchronized."
        )

    @button.buttonAndHandler(u'Add')
    def handleAdd(self, action):
        data, errors = self.extractData()

        if errors:
            return

        response = None
        url = data['url']
        municipality = data.get('municipality', None)

        if 'permalink' in url:
            try:
                response = self._get_article_by_url(url)
            except suds.WebFault:
                self.status = NOT_AN_ARTICLE
        else:
            # try to extract a permalink from document source
            try:
                url = url.split('#', 1)[0]
                logging.debug("Downloading HTML page from %s..." % url)
                html = urllib.urlopen(url).read()
            except IOError:
                self.status = CANT_DOWNLOAD
            else:
                try:
                    soup = bsoup.BeautifulSoup(html)
                except bsoup.HTMLParseError:
                    self.status = CANT_PARSE
                else:
                    link = soup.find(text='Permanent link')

                    if link is not None:
                        url = link.parent['href']

                        if url.startswith('/'):
                            url = 'http://www.borger.dk' + url

                        try:
                            response = self._get_article_by_url(url)
                        except suds.WebFault:
                            self.status = NOT_AN_ARTICLE
                    else:
                        self.status = NO_PERMANENT_LOCATION

        if response is not None:
            try:
                article = self._get_article_by_id(response.ArticleID, municipality)
            except suds.WebFault:
                self.status = SYSTEM_ERROR
            else:
                try:
                    name = self._add_article(article, municipality)
                except BadRequest:
                    self.status = CANT_ADD
                    return
                except AlreadyExists, exc:
                    name = exc.name
                    status(self.request, ALREADY_EXISTS)
                else:
                    status(self.request, ADDED)

                view = self.context.restrictedTraverse('@@plone')
                container = view.getCurrentFolder()
                url = container[name].absolute_url()
                self.request.response.redirect(url)

    @property
    def _client(self):
        return portal.get_client()

    def _get_article_by_url(self, url):
        logging.debug("Requesting article ID from %s..." % url)
        return self._client.service.GetArticleIDByUrl(url)

    def _get_article_by_id(self, _id, municipality):
        logging.debug("Requesting article with ID: %s..." % _id)
        return self._client.service.GetArticleByID(_id, municipality)

    def _add_article(self, article, municipality):
        title = article.ArticleTitle
        name = queryUtility(IURLNormalizer).normalize(title)
        container = self.context.restrictedTraverse('@@plone').getCurrentFolder()

        if name in container.objectIds():
            raise AlreadyExists(name)

        # create document
        name = container.invokeFactory(id=name, type_name='Document')
        document = container[name]

        # set initial content
        update_content(document, article)

        # annotate article metadata
        metadata = get_article_metadata(document)
        metadata.id = article.ArticleID
        metadata.url = article.ArticleUrl
        metadata.municipality = municipality

        # set review state directly (no transition is available for this)
        wftool = getToolByName(self.context, 'portal_workflow')
        status = wftool.getStatusOf('synchronizable_document_workflow', document)
        status['review_state'] = 'synchronized'
        document.reindexObject()

        return name

SynchronizeView = wrap_form(SynchronizeForm)
