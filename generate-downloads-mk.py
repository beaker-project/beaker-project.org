#!/usr/bin/python -B

import sys
import git_tags
print 'DOWNLOADS = \\'
for release in git_tags.releases(sys.argv[1]):
    for download in release.downloads:
        print '    releases/%s \\' % download
print
