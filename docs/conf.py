
# vim: set fileencoding=utf-8 :

# The real conf.py lives in Beaker's source, so we load it from there and then
# override some template settings below.
import os, os.path
execfile(os.path.join(os.environ['BEAKER'], 'documentation', 'conf.py'))

html_theme = 'beaker'
html_theme_path = ['../sphinx-theme']

intersphinx_mapping['python'] = ('http://docs.python.org/',
        os.path.join(os.path.dirname(__file__), '..', 'python-intersphinx.inv'))
intersphinx_mapping['beakerdev'] = ('../dev/',
        os.path.join(os.path.dirname(__file__), '..', 'dev', 'objects.inv'))

keep_warnings = True

html_context = {}
if os.path.basename(os.environ['BEAKER']) == 'master':
    html_context['branch_warning'] = ''
elif os.path.basename(os.environ['BEAKER']) == 'develop':
    html_context['branch_warning'] = u"""
        You are viewing the development version of Beaker’s documentation. It 
        is not final and may be changed before the next release.
        """
else:
    html_context['branch_warning'] = u"""
        You are viewing a branched version of Beaker’s documentation. The 
        latest released version of the documentation contains more 
        up-to-date information.
        """
