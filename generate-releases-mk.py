#!/usr/bin/python -B

import sys

import changelog
print 'DOWNLOADS = \\'
for release in changelog.parse(sys.stdin.read().decode('utf8')):
    for download in release.downloads:
        print '    releases/%s \\' % download
print
