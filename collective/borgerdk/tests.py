from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.borgerdk
    zcml.load_config('configure.zcml', collective.borgerdk)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.borgerdk')

setup_product()
ptc.setupPloneSite(products=['collective.borgerdk'])

class BaseFunctionalTestCase(ptc.FunctionalTestCase):
    test_article_url = "https://www.borger.dk/_layouts/BorgerDK/Permalink/" \
                       "permalink.aspx?PageId=663a8046-3ab6-4d0e-8ec8-" \
                       "f27571137835&KommuneId=101"

    def afterSetUp(self):
        ptc.FunctionalTestCase.afterSetUp(self)

        self.browser = Browser()
        self.browser.handleErrors = False
        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            print info[1]

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising

    def loginAsAdmin(self):
        from Products.PloneTestCase.setup import portal_owner, default_password
        browser = self.browser
        browser.open(self.portal_url + "/login_form")
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()

    def addTestArticle(self):
        self.loginAsAdmin()
        self.browser.open(self.portal_url + "/add-synchronized-document")
        form = self.browser.getForm(index=1)
        form.getControl('Article URL').value = self.test_article_url
        form.getControl('Add').click()

    @property
    def portal_url(self):
        return self.portal.absolute_url()

class PortletTest(BaseFunctionalTestCase):
    def clickAddPortlet(self):
        browser = self.browser
        browser.open(self.portal_url)
        browser.getLink('Manage portlets').click()
        right_column = browser.getForm(index=3)
        right_column.getControl('Borger.dk').selected = True
        right_column.submit()

    def test_add_portlet(self):
        self.loginAsAdmin()
        self.clickAddPortlet()

        # check that we've loaded the municpality list
        municipality = self.browser.getControl('Municipality')

        # choose "Copenhagen Municipality"
        self.assertTrue('101' in municipality.options)
        municipality = self.browser.getControl('Municipality')
        municipality.value = ('101',)

        # add portlet
        self.browser.getControl('Save').click()

    def test_add_article(self):
        self.loginAsAdmin()
        self.test_add_portlet()

        # add new article
        self.browser.open(self.portal_url)
        form = self.browser.getForm(index=1)
        form.getControl('Article URL').value = self.test_article_url
        form.getControl('Add').click()

        # heuristic: the article body always contains the (escaped)
        # permanent article url
        from cgi import escape
        want = escape(self.test_article_url)
        self.assertTrue(want in self.browser.contents)

class ControlPanelTest(BaseFunctionalTestCase):
    def test_synchronize(self):
        # log in as admin and retrieve synchronization url (with token)
        self.loginAsAdmin()
        self.browser.open(self.portal_url + "/@@borger.dk-settings")
        url = self.browser.getLink('@@synchronize').url

        # add test article
        self.addTestArticle()

        # delete article text to prepare tests
        brains = self.portal.portal_catalog(
            portal_type="Document",
            review_state="synchronized"
            )

        document = brains[0].getObject()
        document.setTitle("")

        # log out and visit update url
        self.logout()
        self.browser.open(url)

        # verify that text is now non-trivial
        text = document.getText()
        self.assertNotEqual(text, "")
