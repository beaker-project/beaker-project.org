An example patch: Group name length validation
==============================================

.. highlight:: diff

To get a better sense of how the different modules come together, let's
look at parts of a real patch that has been applied to Beaker. The
`bug <http://bugzilla.redhat.com/show_bug.cgi?id=990349>`_ concerns
inconsistencies in the validation of the group name length and
inconsistency between the database and the validators. 

The group name length was increased to 256 instead of 16 with the
following change in ``model.py``::

    diff --git a/Server/bkr/server/model.py b/Server/bkr/server/model.py
    index 1d92142..023896a 100644
    --- a/Server/bkr/server/model.py
    +++ b/Server/bkr/server/model.py
    @@ -1855,7 +1855,7 @@ class Group(DeclBase, MappedObject, ActivityMixin):
         __table_args__ = {'mysql_engine': 'InnoDB'}
 
         group_id = Column(Integer, primary_key=True)
    -    group_name = Column(Unicode(16), unique=True, nullable=False)
    +    group_name = Column(Unicode(255), unique=True, nullable=False)
         display_name = Column(Unicode(255))
         _root_password = Column('root_password', String(255), nullable=True,
             default=None)

In ``group.py``, the TurboGears validators were updated to retrieve the column
length from the class definition instead of using hard coded values::

    diff --git a/Server/bkr/server/group.py b/Server/bkr/server/group.py
    index cab7d27..da693a4 100644
    --- a/Server/bkr/server/group.py
    +++ b/Server/bkr/server/group.py
    @@ -38,8 +38,12 @@ def set_response(self):
             response.headers['content-type'] = 'application/json'
 
     class GroupFormSchema(validators.Schema):
    -    display_name = validators.UnicodeString(not_empty=True, max=256, strip=True)
    -    group_name = validators.UnicodeString(not_empty=True, max=256, strip=True)
    +    display_name = validators.UnicodeString(not_empty=True,
    +                                            max=Group.display_name.property.columns[0].type.length,
    +                                            strip=True)
    +    group_name = validators.UnicodeString(not_empty=True,
    +                                          max=Group.group_name.property.columns[0].type.length,
    +                                          strip=True)



Using the above validators, we also validate the group name in the
XML-RPC interfaces::

    @@ -735,6 +740,7 @@ def create(self, kw):
             try:
                 group = Group.by_name(group_name)
             except NoResultFound:
    +            GroupFormSchema.fields['group_name'].to_python(group_name)
                 group = Group()
                 session.add(group)
                 activity = Activity(identity.current.user, u'XMLRPC', u'Added', u'Group', u"", kw['display_name'] )
    @@ -813,6 +819,8 @@ def modify(self, group_name, kw):
                     raise BX(_(u'Failed to update group %s: Group name already exists: %s' %
                                (group.group_name, group_name)))

    +            GroupFormSchema.fields['group_name'].to_python(group_name)
    +
             user = identity.current.user
             if not group.can_edit(user):
                 raise BX(_('You are not an owner of group %s' % group_name))


The above validation will raise an ``Invalid`` exception when an
invalid group name is supplied. Hence, we update the
``xmlrpcontroller.py`` module to handle the exception and report the
exception back to the client::

    diff --git a/Server/bkr/server/xmlrpccontroller.py b/Server/bkr/server/xmlrpccontroller.py
    index b0794e2..fb5d9bb 100644
    --- a/Server/bkr/server/xmlrpccontroller.py
    +++ b/Server/bkr/server/xmlrpccontroller.py
    @@ -7,6 +7,7 @@
     from turbogears import controllers
     from turbogears.database import session
     from turbogears.identity.exceptions import IdentityFailure, get_identity_errors
     +from formencode.api import Invalid
 
     log = logging.getLogger(__name__)
 
    @@ -65,6 +66,9 @@ def RPC2(self, *args, **kw):
                 log.exception('Error handling XML-RPC method')
                 # Can't marshal the result
                 response = xmlrpclib.dumps(fault)
    +        except Invalid, e:
    +             session.rollback()
    +             response = xmlrpclib.dumps(xmlrpclib.Fault(1, str(e)))
             except:
                 session.rollback()
                 log.exception('Error handling XML-RPC method')

Since both the XML-RPC and the Web UI were affected by the bug, tests
were added for both the interfaces. One of the tests to test the
XML-RPC interface was::

    diff --git a/IntegrationTests/src/bkr/inttest/client/test_group_create.py b/IntegrationTests/src/bkr/inttest/client/test_group_create.py
    index dfbed2b..5e60785 100644
    --- a/IntegrationTests/src/bkr/inttest/client/test_group_create.py
    +++ b/IntegrationTests/src/bkr/inttest/client/test_group_create.py
    @@ -1,4 +1,4 @@
    -import unittest
    +import unittest2 as unittest
     from turbogears.database import session
     from bkr.server.model import Activity, Group, User
     from bkr.inttest import data_setup

    @@ -47,6 +47,14 @@ def test_group_create(self):
             except ClientError,e:
                 self.assert_('Exactly one group name must be specified' in
                              e.stderr_output, e.stderr_output)
    +        try:
    +            out = run_client(['bkr', 'group-create',
    +                              'areallylonggroupname'*20])
    +            self.fail('Must fail or die')
    +        except ClientError,e:
    +            max_length = Group.group_name.property.columns[0].type.length
    +            self.assertIn('Enter a value less than %r characters long' %
    +                          max_length, e.stderr_output)
 

A Selenium test was added to test the Web UI for creating and
modifying groups. 

The change to ``model.py`` in this patch means that the database
schema have to be updated appropriately. Hence, for this patch (and
for such patches), the appropriate SQL queries to effect the change and
rollback (in case something goes wrong) should also be included as
part of the patch. For this patch, the SQL query to effect the change
was::

    ALTER TABLE tg_group MODIFY group_name VARCHAR(255);

The query to rollback the change was::

    ALTER TABLE tg_group MODIFY group_name VARCHAR(16);

The entire patch can be seen `here
<http://git.beaker-project.org/cgit/beaker/commit/?h=develop&id=1b2e8bd80e90733a04948aaa35f68be25fd1b612>`__.
