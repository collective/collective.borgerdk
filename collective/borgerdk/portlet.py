import random
import time

from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import alsoProvides
from zope import schema
from zope.formlib import form
from zope.security import checkPermission

from z3c.form import widget
from z3c.form.interfaces import HIDDEN_MODE

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager
from collective.borgerdk import MessageFactory as _

from .form import SynchronizeForm
from .form import ILocalization

class IBorger(IPortletDataProvider, ILocalization):
    pass

class Assignment(base.Assignment):
    implements(IBorger)

    def __init__(self, municipality=None):
        self.municipality = municipality

    @property
    def title(self):
        return u"Borger.dk"

class AddForm(base.AddForm):
    form_fields = form.Fields(IBorger)

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IBorger)

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('portlet.pt')

    def update(self):
        self.form = SynchronizeForm(self.context, self.request)

        # set municipality on form
        self.form.municipality = self.data.municipality
        alsoProvides(self.form, ILocalization)

        # update form
        self.form.update()

        # hide municipality widget if set
        if self.data.municipality is not None:
            self.form.widgets['municipality'].mode = HIDDEN_MODE

    def render(self):
        return self._template()

    @property
    def available(self):
        view = getMultiAdapter((self.context, self.request), name=u'plone')
        container = view.getCurrentFolder()

        if not checkPermission('cmf.AddPortalContent', container):
            return

        pt = getToolByName(self.portal, 'portal_types')
        my_type = pt.getTypeInfo(container)

        return my_type.allowType('Document')

    @property
    def portal(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        return portal_state.portal()

    @property
    def portal_url(self):
        return self.portal.absolute_url()

    @property
    def title(self):
        return self.data.title

def get_municipality_from_view(adapter):
    return adapter.view.municipality

DefaultMunicipality = widget.ComputedWidgetAttribute(
    get_municipality_from_view, field=ILocalization['municipality'],
    view=ILocalization,
    )
