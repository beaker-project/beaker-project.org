
# The real conf.py lives in Beaker's source, so we load it from there and then
# override some template settings below.
import os, os.path
execfile(os.path.join(os.environ['BEAKER'], 'Client', 'doc', 'conf.py'))

html_theme = 'basic'
html_theme_options = {'nosidebar': True}
pygments_style = 'sphinx'
templates_path = ['../sphinx-templates']
