from zope.interface import Interface
from zope import schema

from collective.borgerdk import MessageFactory as _

class IBorgerPortalSettings(Interface):
    url = schema.TextLine(
        title=_(u"URL to the SOAP web service"),
        default=u"http://ressourcer.borger.dk/ArticleExport/ArticleExport.svc?wsdl",
        required=True
        )

    synchronization_token = schema.TextLine(
        title=_(u"Synchronization token"),
        description=_(u"Use this token to update all synchronized documents."),
        readonly=True,
        required=False,
        )
