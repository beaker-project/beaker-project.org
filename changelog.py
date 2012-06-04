
import re
import datetime

BAD_VER_RELS = [
    # divergent, so they don't produce a usable patch series
    '0.8.0-24.1',
    '0.8.1-5.1',
    '0.8.1-5.2',
    # pre-releases, not real releases that we want people to use
    '0.8.99-1',
    '0.8.99-2',
    '0.8.99-3',
]

# Is there any better parser we could use here??? e.g. from rpm

class Release(object):

    def __init__(self, version, release, date, changes):
        self.version = version
        self.release = release
        self.date = date
        self.changes = changes

    @property
    def downloads(self):
        if self.release != '-1':
            return ['beaker-%s%s.patch' % (self.version, self.release)]
        else:
            return ['beaker-%s.tar.gz' % self.version,
                    'beaker-%s.tar.xz' % self.version]

def parse(spec):
    _, _, changelog = spec.partition('\n%changelog\n')
    releases = re.split(r'(?m)(^\*.*$)', changelog)
    releases.pop(0) # empty string
    while releases:
        date, releaser, ver, rel = re.match(
                r'\* \w{3} (\w{3} \d+ \d{4}) (.*?) ([\d.]+)(-.*)?',
                releases.pop(0)).groups()
        changes = [c.replace('%%', '%') for c in re.split(r'(?m)^- ', releases.pop(0)) if c.split()]
        if ver + rel in BAD_VER_RELS:
            continue
        date = datetime.datetime.strptime(date, '%b %d %Y').date()
        yield Release(ver, rel, date, changes)
        if (ver, rel) == ('0.6.2', '-1'):
            break # don't bother with the really old stuff
