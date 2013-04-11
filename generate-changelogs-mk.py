#!/usr/bin/python -B

import sys
import git_tags
versions = [r.version for r in git_tags.releases(sys.argv[1])] + ['0.9.4']
changelogs = []
for i in xrange(len(versions) - 1):
    changelog = 'releases/beaker-%s-ChangeLog' % versions[i]
    print '%s: changelogs.mk git_tags.py' % changelog
    print '\tGIT_DIR=$(BEAKER_GIT) git log --no-notes --no-merges ' \
          'beaker-%s-1..beaker-%s-1 >$@' % (versions[i + 1], versions[i])
    changelogs.append(changelog)
print 'CHANGELOGS = %s' % ' '.join(changelogs)
