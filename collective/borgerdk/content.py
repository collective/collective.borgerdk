from DateTime import DateTime
from zope.annotation.interfaces import IAnnotations


def get_article_metadata(document):
    return IAnnotations(document).setdefault('borger.dk', Metadata())


def is_synchronized(wftool, document):
    status = wftool.getStatusOf('synchronizable_document_workflow', document)
    return status and status['review_state'] == 'synchronized'


def update_content(document, article):
    document.setTitle(article.ArticleTitle.encode('utf-8'))
    document.setDescription(article.ArticleHeader.encode('utf-8'))
    document.setText(article.Content.encode('utf-8'))
    document.setEffectiveDate(DateTime(article.PublishingDate))
    document.setModificationDate(DateTime(article.LastUpdated))


class Metadata(object):
    """Holds article metadata."""

    id = url = municipality = None
