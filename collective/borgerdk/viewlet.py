from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from collective.borgerdk.content import get_article_metadata
from collective.borgerdk.content import is_synchronized

class LinkToSourceViewlet(object):
    render = ViewPageTemplateFile("link.pt")

    def get_url(self):
        metadata = get_article_metadata(self.context)
        return metadata.url

    def is_synchronized(self):
        wftool = getToolByName(self.context, 'portal_workflow')
        return is_synchronized(wftool, self.context)
