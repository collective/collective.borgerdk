from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.borgerdk',
      version=version,
      description="Synchronize content between Plone site and the borger.dk portal.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='web zope plone integration borger.dk',
      author='Malthe Borch and Headnet',
      url='http://svn.headnet.dk/shiny/collective.borgerdk',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.z3cform',
          'suds',
          'BeautifulSoup',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
