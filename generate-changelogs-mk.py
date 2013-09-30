#!/usr/bin/python -B

import sys
import git_tags
versions = [(r.version, r.tag) for r in git_tags.releases(sys.argv[1])] + [('0.9.4', 'beaker-0.9.4-1')]
changelogs = []
for i in xrange(len(versions) - 1):
    changelog = 'releases/beaker-%s-ChangeLog' % versions[i][0]
    print '%s: changelogs.mk git_tags.py' % changelog
    print '\tGIT_DIR=$(BEAKER_GIT) git log --no-notes --no-merges ' \
          '%s..%s >$@' % (versions[i + 1][1], versions[i][1])
    changelogs.append(changelog)
print 'CHANGELOGS = %s' % ' '.join(changelogs)
