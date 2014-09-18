Coding guidelines
=================

This page summarizes some of the guidelines that should be helpful
while adding new code to Beaker.

Model
~~~~~

From version 0.16 onwards, Object Relational Mapped classes should be defined 
`declaratively
<http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html>`__. Previous
versions used `Classical Mapping
<http://docs.sqlalchemy.org/en/rel_0_7/orm/mapper_config.html#classical-mappings>`__ 
for some classes.

Some basic guidelines to follow when modifying model:

-  Commonly used queries should be encapsulated as class methods of the
   respective classes or using `hybrid attributes
   <http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/hybrid.html>`__.
-  Enumerated types should be defined as type DeclEnum and not be
   described in a database schema. This helps avoid over normalization,
   cuts down on unnecessary calls to the database, and reduces the
   likelihood of complex joins that confuse the query optimizer. This
   only applies though if it's an enumeration that is static.
-  When writing queries, use ORM attributes over `SQL Expression
   Language
   <http://docs.sqlalchemy.org/en/rel_0_7/core/tutorial.html?highlight=sql%20expression%20language>`__
   whenever possible, and never use `Text <http://docs.sqlalchemy.org/en/rel_0_7/core/types.html>`__.
-  Write efficient queries. Do what you can to write the most reasonably
   efficient query. For various reasons, Beaker has few options of
   removing its historical data. Thus, dataset can only increase in size
   over time. As Beaker's UI relies heavily on database  
   calls, writing inefficient queries can quickly become a bottleneck
   and create a marked reduction in usability.
-  Beyond the basic relationship mapping, relationships should be
   defined keeping performance in mind. The sqlalchemy documentation
   provides some good
   `ideas <http://docs.sqlalchemy.org/en/rel_0_7/orm/collections.html>`_.
-  Remember to define relevant cascade options.


Database column defaults
~~~~~~~~~~~~~~~~~~~~~~~~

For database columns with `default values 
<http://docs.sqlalchemy.org/en/rel_0_7/core/schema.html#column-insert-update-defaults>`__, 
always use a Python-level default: pass a scalar or Python callable as the 
*default* parameter for the :py:class:`Column() <sqlalchemy.schema.Column>` 
constructor.

Note that this means the default value will *not* appear on the column 
definition in the database schema. Schema upgrade notes which add a new column 
with a default value should look like this (note no ``DEFAULT`` clause)::

    ALTER TABLE power ADD COLUMN power_quiescent_period INT NOT NULL;
    UPDATE power SET power_quiescent_period = 5;

Do not use server-side column defaults (*server_default* parameter, or 
*default* with a SQL expression). That way we avoid defining the default value 
in two places (model code and the database schema); Beaker can skip the extra 
database round-trip to fetch the generated defaults, which might be expensive 
in some cases; and we have one consistent mechanism for defining column 
defaults throughout the application.


Controller methods
~~~~~~~~~~~~~~~~~~

Starting with Beaker 0.15, the Beaker server uses Flask. The Flask
application instance, ``app`` needs to be imported from ``bkr.server.app``
and then the view function can be exposed by decorating it with
``@app.route()``. You can also specify the HTTP methods which the view can
handle using the methods keyword argument. Example::

    @app.route('/systems/<fqdn>/access-policy', methods=['POST','PUT'])

To learn more about Flask routing, see `here
<http://flask.pocoo.org/docs/api/#url-route-registrations>`__.

CherryPy is embedded inside Flask to support the large number of
legacy TurboGears controllers which still exist in Beaker. New code
should not use TurboGears or CherryPy unless necessary.

In most controller methods, you may need to perform one or more of the
following functions:

- *Authentication*: If a view function requires authentication, it should
  be decorated using the ``bkr.server.flask_util.auth_required``
  decorator (added in Beaker 0.15.2).

- *Returning data*: Use Flask's ``jsonify()`` function to return your response
  as JSON objects. To learn more, see `here
  <http://flask.pocoo.org/docs/api/#module-flask.json>`__.

- *Aborting*: If something is not right, raise an appropriate
  exception from one of the exception classes defined in
  ``bkr.server.flask_util`` (starting with Beaker 0.15.2). For
  example, ``raise NotFound404('System not found')``. If an
  appropriate exception is not found, please add one in this module
  along with your patch.

- *Empty response*: If the view function has nothing to return,
  return an empty string with a status code, like so: ``return '',
  204``.

.. _api-stability:

API compatibility
~~~~~~~~~~~~~~~~~

To avoid unnecessary churn for our users, Beaker maintains API compatibility 
across all maintenance releases in a series (for example 19.0, 19.1, …). Any 
patches in a maintenance release must not break API compatibility.

APIs can be removed (if absolutely necessary) only after they have been through 
a deprecation period of at least one release. This entails updating all 
relevant documentation and code to mark the API as deprecated in version N, and 
then removing it no sooner than version N+1.

These guidelines apply specifically to (programmatic) HTTP interfaces, XML-RPC
interfaces, and the bkr client.

Client–server compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The bkr client must be backwards compatible with at least the previous version 
of the server (for example, client 20.x must be compatible with server 19.x). 
New commands are excluded from this requirement.

Also note that the bkr client itself is considered an API for scripting 
purposes, so it must also maintain API compatibility with older versions of 
itself as described above.

Logging Activities
~~~~~~~~~~~~~~~~~~

If an activity needs to be logged, use the ``ActivityMixin`` methods to
record it. For example::

     system.record_activity(user=identity.current.user,
             service=u'HTTP',field=u'Access Policy Rule', action=u'Removed')


However, for this to be possible, the ORM class should inherit the
``ActivityMixin`` class and define an ``activity_type`` attribute set
to the ``Activity`` subclass to use, like so::

    class User(MappedObject, ActivityMixin):
        @property
        def activity_type(self):
            return UserActivity
    # class definition

Writing tests
~~~~~~~~~~~~~

The `unittest2 <https://pypi.python.org/pypi/unittest2>`__ package
adds a number of additional convenience methods and hence should be
preferred for new tests. All existing and new tests should import it
as : ``import unittest2 as unittest``.

New selenium tests should use ``webdriver`` via
``WebDriverTestCase``.
