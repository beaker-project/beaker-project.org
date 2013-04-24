
extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinxcontrib.httpdomain',
]
master_doc = 'index'
project = u'Beaker'
copyright = u'2013, Red Hat, Inc'

release = version = "Project"

html_title = 'Beaker'
html_use_index = False
html_domain_indices = False
html_theme = 'basic'
html_theme_options = {'nosidebar': True}
pygments_style = 'sphinx'
templates_path = ['../sphinx-templates']


intersphinx_mapping = {'python': ('http://docs.python.org/',
                                  '../python-intersphinx.inv'),
                      }

# This config is also a Sphinx extension with some Beaker-specific customisations:

import docutils.core, docutils.nodes

# A poor man's version of sphinxcontrib-issuetracker 
# <https://pypi.python.org/pypi/sphinxcontrib-issuetracker> which unfortunately 
# requires a newer python-requests than is available in Fedora.
# This code inspired by Doug Hellman's article 
# <http://doughellmann.com/2010/05/defining-custom-roles-in-sphinx.html>.
def beaker_bugzilla_issue_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    bz_url = 'https://bugzilla.redhat.com/show_bug.cgi?id=%s' % text
    node = docutils.nodes.reference(rawtext, text, refuri=bz_url, **options)
    return [node], []

def setup(app):
    app.add_role('issue', beaker_bugzilla_issue_role)
