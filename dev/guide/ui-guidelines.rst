
.. _ui-guidelines:

User interface guidelines
=========================

.. note::

   Most of Beaker's user interface does not currently meet these guidelines, 
   due to limitations of the technology stack or historical inconsistencies. 
   These guidelines are for new code and describe a state we aim to achieve, 
   rather than the current state of the code.

Convey information naturally
----------------------------

Most of the data in Beaker is viewed much more often than it is edited. Design 
the interface first and foremost to convey the data in the most natural way 
possible; aim for convenience, conciseness, discoverability, and consistency. 
Display simple facts as a phrase or sentence. For a list of homogeneous items, 
use a list. Use a table for tabular data. Position the most important data 
prominently, and less important data unobtrusively (even hidden by default), 
but above all else keep the positions consistent. Emphasize a piece of 
information only if it is unusual or unexpected.

If there is only a small number of possible operations to be performed on the 
data, consider adorning the data directly with unobtrusive buttons to trigger 
these operations. Otherwise, use a single button to trigger a separate 
interface for editing the data (often inside a modal). In the editing 
interface, the data is displayed in the most convenient way for editing it: 
often, a form.

It is tempting to design a form for the data first, and then present a view of 
that data as a form with disabled fields. Avoid this approach; a form is rarely 
the best layout for conveying information, and disabled form fields are 
difficult to read.

Indicate status of server requests
----------------------------------

In Beaker a button will typically trigger a server request. While the request 
is in progress, the button which triggered it is disabled and a status message 
appears near the trigger indicating that a request is in progress. Use 
a spinner plus a phrase that describes the action being performed 
("Lending...") rather than the mechanics of the request ("Sending server 
request...").

When the server request completes, the trigger returns to its normal state and 
the interface is ready to accept input again. The view is updated with the new 
state reflecting the completed action. If the action does not cause any visible 
changes, a success notification is displayed instead (but this is less 
desirable).

If the server request fails, an error is displayed near the trigger. The error 
text includes any messages returned by the server.

Use Bootstrap components
------------------------

Bootstrap provides a consistent framework for many common UI components which 
appear in web applications. Use them all to the fullest extent possible.

Use a `button <http://getbootstrap.com/2.3.2/base-css.html#buttons>`_ for an 
action that the user can trigger. Label the button with a verb phrase 
indicating the action it will trigger. Use a hyperlink to link to other 
material or pages. Use a noun phrase as the anchor text.

Group related actions together as a `button group 
<http://getbootstrap.com/2.3.2/components.html#buttonGroups>`_.

Use `alerts <http://getbootstrap.com/2.3.2/components.html#alerts>`_ only when 
the user's attention must be drawn to something in particular: a change that 
has just taken place, a condition out of the ordinary, a failed action.

Capitalize appropriately
------------------------

Use sentence case for all UI elements, except the following which should be 
labelled in title case:

* buttons
* tabs
* menus and menu items
* column headings
