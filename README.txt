Overview
========

This package adds a portlet that lets users create a document which
synchronizes its content with an article on the borger.dk portal.

A new document workflow is included which adds a workflow state
"Synchronized". There is no public transition to reach this state;
instead, a portlet user interface is presented to allow users to
create new synchronized documents. The setup profile applies this
workflow to the existing document type.

User interface
==============

The package adds a control panel setting and a portlet.

Control panel

  This lets an administrator select the service URL.

Portlet

  With a configurable municipality setting, the portlet allows a user
  with document creation privileges to add a synchronized document
  tied to a municipality location.

  The user selects the remote article by entering a URI for an article
  on the borger.dk portal.

  If the document is not already a permanent location, the handler
  will attempt to locate the permanent location by looking for an HTML
  link with the text "Permanent".

  The document will be added to the current container (using
  ``getCurrentFolder()``) with an id decided by the ``IURLNormalizer``
  utility.

Technical details
=================

Synchronization

  The synchronization view updates all synchronized content.

  Access to this view is via a self-authenticating URL which is
  visible in the control panel.

Caching

  The SOAP client object is cached as a volatile attribute on the
  portal object.

