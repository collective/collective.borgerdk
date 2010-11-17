from plone.app.registry.browser import controlpanel
from collective.borgerdk import MessageFactory as _
from z3c.form import field
from z3c.form import widget
from z3c.form.browser import text

from .interfaces import IBorgerPortalSettings

class SynchronizationTokenWidget(text.TextWidget):
    @classmethod
    def factory(cls, field, request):
        return widget.FieldWidget(field, cls(request))

    def render(self):
        url = self.form.context.absolute_url() + "/@@synchronize?token=%s" % \
              self.context.synchronization_token

        return u'<a href="%s">%s</a>' % (url, url)

class PortalEditForm(controlpanel.RegistryEditForm):
    schema = IBorgerPortalSettings
    fields = field.Fields(schema)
    fields['synchronization_token'].widgetFactory = SynchronizationTokenWidget.factory
    label = _(u"Borger.dk portal settings")

class BorgerPortalControlPanel(controlpanel.ControlPanelFormWrapper):
    form = PortalEditForm
