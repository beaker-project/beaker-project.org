Coding guidelines
=================

This page summarizes some of the guidelines that should be helpful
while adding new code to Beaker.

Model
~~~~~

From version 0.11 Object Relational Mapped classes should be defined `declaratively
<http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html>`__. Previous
versions used `Classical Mapping
<http://docs.sqlalchemy.org/en/rel_0_7/orm/mapper_config.html#classical-mappings>`__.

Some basic guidelines to follow when modifying model:

-  For versions < 0.11, definitions of Tables, ORM classes, and calls to
   ``mapper()`` are segregated into three distinct sections. Tables are
   defined above ORM classes, and ORM classes above mapper functions. If
   possible define related Tables in the vicinity of each other, and
   likewise for ORM classes and mappers.
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

- *Authentication*: If a view function needs authentication,
  you can use the ``bkr.server.identity`` module.

- *Retuning data*: Use Flask's ``jsonify()`` function to return your response
  as JSON objects. To learn more, see `here
  <http://flask.pocoo.org/docs/api/#module-flask.json>`__.

- *Aborting*: If something is not right, use the ``abort()`` function
  to raise a HTTPException. For eg, abort(403) would indicate a
  request to a forbidden resource. To learn more, see `here
  <http://flask.pocoo.org/docs/api/#flask.abort>`__.

- *Empty response*: If the view function has nothing to return,
  return an empty string with a status code, like so: ``return '',
  204``.

Logging Activities
~~~~~~~~~~~~~~~~~~

If an activity needs to be logged, use the ``ActivityMixin`` methods to
record it. For example::

     system.record_activity(user=identity.current.user,
             service=u'HTTP',field=u'Access Policy Rule', action=u'Removed')


However, for this to be possible, the ORM class should inherit the
``ActivityMixin`` class and define an ``activity_type`` attribute set
to the ``Acitivity`` subclass to use, like so::

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
