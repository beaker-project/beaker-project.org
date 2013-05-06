An example patch: removing tasks
================================

.. highlight:: diff

To get a better sense of how the different modules come together, let's
look at parts of a real patch that has been applied to Beaker. The
`bug <http://bugzilla.redhat.com/show_bug.cgi?id=590033>`_ is an RFE to
remove tasks from the task library.

Let's look at what we have to do in ``model.py`` first.

::

    diff --git a/Server/bkr/server/model.py b/Server/bkr/server/model.py
    index bd2995d..ae8de19 100644
    --- a/Server/bkr/server/model.py
    +++ b/Server/bkr/server/model.py
    @@ -1002,7 +1002,7 @@
                    ForeignKey('tg_user.user_id')),
             Column('version', Unicode(256)),
             Column('license', Unicode(256)),
    -        Column('valid', Boolean),
    +        Column('valid', Boolean, default=True),
             mysql_engine='InnoDB',
    )

We need to change our Table instance so that newly created tasks are
valid by default. This table's schema is created from the 'beaker-init'
command, which is only run when setting up a new beaker environment, or
when there are new tables to create. We will need to update the current
schema in the DB manually, but we will look at that later.

::

    @@ -5845,9 +5845,23 @@ class Task(MappedObject):
         """
         Tasks that are available to schedule
         """
    +    @property
    +    def task_dir(self):
    +        return get("basepath.rpms", "/var/www/beaker/rpms")
    +
         @classmethod
    -    def by_name(cls, name):
    -        return cls.query.filter_by(name=name).one()
    +    def by_name(cls, name, valid=None):
    +        query = cls.query.filter(Task.name==name)
    +        if valid:
    +            query = query.filter(Task.valid==bool(valid))
    +        return query.one()
    +
    +    @classmethod
    +    def by_id(cls, id, valid=None):
    +        query = cls.query.filter(Task.id==id)
    +        if valid:
    +            query = query.filter(Task.valid==bool(valid))
    +        return query.one()

``by_name()`` and ``by_id()`` are commonly implemented methods for
querying the database. These also need to be updated so we can specify
whether we want valid or invalid tasks to be returned.

::

    @@ -5919,6 +5933,17 @@ def elapsed_time(self, suffixes=[' year',' week',' day',' hour',' minute',' seco

             return separator.join(time)

    +    def disable(self):
    +        """
    +        Disable task so it can't be used.
    +        """
    +        for rpm in [self.oldrpm, self.rpm]:
    +            rpm_path = "%s/%s" % (self.task_dir, rpm)
    +            if os.path.exists(rpm_path):
    +                os.unlink(rpm_path)
    +        self.valid=False
    +        return
    +

A cohesive method that will handle the details of disabling a task is
desirable. This method acts directly on the ``Task`` object and will be
called by a controller.

::

    @@ -1469,7 +1469,33 @@ def display(self, task, **params):
         return super(RecipeActionWidget,self).display(task, **params)


    -class JobActionWidget(TaskActionWidget):
    +class TaskActionWidget(RPC):
    +    template = 'bkr.server.templates.task_action'
    +    params = ['redirect_to']
    +    action = url('/tasks/disable_from_ui')
    +    javascript = [LocalJSLink('bkr', '/static/javascript/task_disable.js')]
    +
    +    def __init__(self, *args, **kw):
    +        super(TaskActionWidget, self).__init__(*args, **kw)
    +
    +    def display(self, task, action=None, **params):
    +        id = task.id
    +        task_details={'id': 'disable_%s' % id,
    +            't_id' : id}
    +        params['task_details'] = task_details
    +        if action:
    +            params['action'] = action
    +        return super(TaskActionWidget, self).display(task, **params)
    +
    +    def update_params(self, d):
    +        super(TaskActionWidget, self).update_params(d)
    +        d['task_details']['onclick'] = "TaskDisable('%s',%s, %s)" % (
    +            d.get('action'),
    +            jsonify.encode({'t_id': d['task_details'].get('t_id')}),
    +            jsonify.encode(self.get_options(d)),
    +            )
    +

A widget enables us to encapsulate code that renders a template.
Typically, various arguments are passed to the widget's display method.
This data is often used to determine what will actually be displayed.

Widgets should be stateless. Data that is to be rendered by the widget
should be passed to the ``display()`` method, not to the widget's
constructor.

Note that we've also added a new javascript file, ``task_disable.js``.
If this widget is to be returned in a controller, this javascript source
file would be linked into the DOM for us.

Although not always necessary, widgets are a good way to harness code
re-usability.

::

    diff --git a/Server/bkr/server/templates/task_action.kid b/Server/bkr/server/templates/task_action.kid
    new file mode 100644
    index 0000000..5c0ea33
    --- /dev/null
    +++ b/Server/bkr/server/templates/task_action.kid
    @@ -0,0 +1,7 @@
    +<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    +<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
    +<div>
    +<a py:if="'admin' in tg.identity.groups" class='list' style='cursor:pointer;color: #22437f;' py:attrs='task_details'>Disable</a><br/>
    +</div>
    +
    +</html>

This is the template that the ``TaskActionWidget`` renders. Notice how
variables such as ``task_details`` are passed from the widget to the
template, via the ``params`` arg.

::

    diff --git a/Server/bkr/server/tasks.py b/Server/bkr/server/tasks.py
    index 2fe447b..21b1afd 100644
    --- a/Server/bkr/server/tasks.py
    +++ b/Server/bkr/server/tasks.py
    @@ -25,6 +25,7 @@
     from bkr.server.widgets import TasksWidget
     from bkr.server.widgets import TaskSearchForm
     from bkr.server.widgets import SearchBar
    +from bkr.server.widgets import TaskActionWidget
     from bkr.server.xmlrpccontroller import RPCRoot
     from bkr.server.helpers import make_link
     from bkr.server import testinfo
    @@ -50,9 +51,10 @@ class Tasks(RPCRoot):
         # For XMLRPC methods in this class.
         exposed = True

    +    task_list_action_widget = TaskActionWidget()

``tasks.py`` is our controller module for actions on the '/tasks' page.
We import our widget here and instantiate it.

::

    @@ -315,6 +354,7 @@ def index(self, *args, **kw):
                         widgets.PaginateDataGrid.Column(name='name', getter=lambda x: make_link("./%s" % x.id, x.name), title='Name', options=
                         widgets.PaginateDataGrid.Column(name='description', getter=lambda x:x.description, title='Description', options=dict(s
                         widgets.PaginateDataGrid.Column(name='version', getter=lambda x:x.version, title='Version', options=dict(sortable=True
    +                    widgets.PaginateDataGrid.Column(name='action', getter=lambda x: self.task_list_action_widget.display(task=x, type_='t
                         ])

Although perhaps not a typical example, here the widget's ``display()``
method is called from a lambda function and will be rendered inside the
task grid. More often the widget is returned from a controller and its
``display()`` method called in the template.

::

    diff --git a/SchemaUpgrades/upgrade_0.6.11.txt b/SchemaUpgrades/upgrade_0.6.11.txt
    new file mode 100644
    index 0000000..c9f565e
    --- /dev/null
    +++ b/SchemaUpgrades/upgrade_0.6.11.txt
    @@ -0,0 +1,8 @@
    +Make task.valid default True
    +---------------------------------
    +UPDATE task set valid = True;
    +ALTER TABLE task MODIFY valid TINYINT DEFAULT 1;
    +
    +To roll back:
    +   Nothing is needed, it doesn't hurt to leave the task valid=true.
    +

As previously mentioned, we will need to manually update the database to
reflect the new schema changes introduced. We do this in the
``SchemaUpgrades`` directory, in a file named ``upgrade_<version>.txt``.
Despite the name of the parent directory, this is the place to put any
manual upgrades that are needed as part of an upgrade. Note that roll
back code should also be included if it makes sense to do so.
