
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


intersphinx_mapping = {'http://docs.python.org/': None,
                       'http://beaker-project.org/docs/': None}
