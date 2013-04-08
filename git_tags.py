
import re
from itertools import takewhile
import datetime
import dulwich.repo
from dateutil.tz import tzoffset

class Release(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @property
    def downloads(self):
        return ['beaker-%s.tar.gz' % self.version,
                'beaker-%s.tar.xz' % self.version]

    @property
    def changelog_href(self):
        return 'beaker-%s-ChangeLog' % self.version

    @property
    def minor(self):
        return '.'.join(self.version.split('.')[:2])

def releases(git_dir):
    repo = dulwich.repo.Repo(git_dir)
    releases = []
    # XXX limit to tags reachable from refs/heads/master!
    for tag_name in repo.refs.keys('refs/tags/'):
        m = re.match(r'beaker-([\d.]*)-1', tag_name)
        if not m:
            continue
        version = m.group(1)
        tag = repo.get_object(repo.refs['refs/tags/%s' % tag_name])
        if tag.type_name != 'tag':
            continue # lightweight
        name, email = re.match(r'(.*) <(.*)>', tag.tagger).groups()
        timestamp = datetime.datetime.fromtimestamp(tag.tag_time,
                tzoffset(None, tag.tag_timezone))
        releases.append(Release(version=m.group(1), timestamp=timestamp,
                name=name, email=email))
    releases = sorted(releases, key=lambda r: r.timestamp, reverse=True)
    # skip anything prior to 0.10
    releases = list(takewhile(lambda r: r.version != '0.9.4', releases))
    return releases
