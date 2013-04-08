#!/usr/bin/python -B
# vim: set fileencoding=utf8 :

"""
Writes out the Releases page (or feed) to stdout, based on tags in Beaker's git.
"""

import sys
import re
import datetime
from itertools import groupby, takewhile
import lxml.html
from genshi import Markup
from genshi.template import MarkupTemplate

import git_tags

def minor_blurb(minor):
    section_id = 'beaker-%s' % (minor.replace('.', '-'))
    tree = lxml.html.parse('docs/whats-new/index.html')
    blurb = tree.find('//div[@id="%s"]/p[1]' % section_id)
    if blurb is None:
        return None
    if len(blurb):
        blurb[-1].tail = (blurb[-1].tail or '') + ' '
    else:
        blurb.text = (blurb.text or '') + ' '
    more_link = lxml.html.Element('a', style='font-style: italic;', href='../docs/whats-new/#%s' % section_id)
    more_link.text = u'(more\u2026)'
    blurb.append(more_link)
    return Markup(lxml.html.tostring(blurb))

_sha1sums = dict((line[42:].rstrip('\n'), line[:40]) for line in open('releases/SHA1SUM'))
def sha1(filename):
    return _sha1sums[filename]

html_template = MarkupTemplate('''
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://genshi.edgewall.org/">
<head>
  <title>Beaker releases</title>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width" />
  <!--[if lt IE 9]>
    <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
  <![endif]-->
  <link href="../style.css" rel="stylesheet" type="text/css"/>
  <style type="text/css">
    article {
        margin-bottom: 1em;
    }
    .release h2 {
        display: inline-block;
        font-size: 1em;
    }
    .date:before, .changelog-link:before {
        content: "·";
        margin-right: 0.3em;
    }
    .date, .changelog-link {
        display: inline-block;
        margin-left: 0.4em;
    }
    .download {
        margin: 0.5em 0;
        background-position: left top;
        background-repeat: no-repeat;
        padding-left: 74px;
    }
    .download.tarball {
        background-image: url("../images/package.png");
        min-height: 54px;
    }
    .download.patch {
        background-image: url("../images/patch.png");
        min-height: 64px;
    }
    .hash {
        white-space: nowrap;
        font-size: 0.9em;
    }
  </style>
  <link rel="profile" href="http://microformats.org/profile/hatom" />
  <link rel="alternate" type="application/atom+xml" title="Atom feed" href="index.atom" />
</head>
<body>
<div class="header">
  <div class="body_element">
    <div class="title">
      <a href="../"><img src="../images/logo.png" alt="Beaker" width="110" height="40" /></a>
    </div>
    <nav class="menu">
      <a href="../">about</a>
      <a href="../help.html">help</a>
      <a href="../download.html">download</a>
    </nav>
  </div>
</div>
<div class="main_content">
  <div class="body_element">

<h1>Releases</h1>

<section py:for="minor, releases in groupby(releases, lambda r: r.minor)">
<h2>Beaker ${minor}</h2>
${minor_blurb(minor)}

<article class="release hentry" py:for="release in releases" id="beaker-${release.version}-1">
    <h2 class="entry-title">Beaker ${release.version}</h2>
    <div class="date">
        <time datetime="${release.timestamp}" pubdate="pubdate">${release.timestamp.strftime('%-1d %B %Y')}</time>
    </div>
    <div class="changelog-link">
        <a href="${release.changelog_href}">Change log</a>
    </div>
    <div class="author vcard">
        <span class="fn" title="${release.name}" />
        <a class="email" href="mailto:${release.email}" />
    </div>
    <div class="downloads entry-content">
        <p py:for="download in release.downloads"
           class="download ${'.tar' in download and 'tarball' or ''} ${'.patch' in download and 'patch' or ''}">
            <a href="${download}">${download}</a><br />
            <span class="hash">SHA1: <tt>${sha1(download)}</tt></span>
        </p>
    </div>
</article>

</section>

<p>For older releases, please refer to
<a href="http://git.beaker-project.org/cgit/beaker/">Beaker’s git repo</a>.</p>

  </div>
</div>
</body>
</html>
''')

atom_template = MarkupTemplate('''
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:py="http://genshi.edgewall.org/">
<id>http://beaker-project.org/releases/index.atom</id>
<title type="text">Beaker releases</title>
<link rel="self" type="application/atom+xml" href="http://beaker-project.org/releases/index.atom" />
<link rel="alternate" href="http://beaker-project.org/releases/" />

<entry py:for="release in releases">
    <id>http://beaker-project.org/releases/#beaker-${release.version}-1</id>
    <published>${release.timestamp.isoformat('T')}</published>
    <author>
        <name>${release.name}</name>
        <email>${release.email}</email>
    </author>
    <title type="text">Beaker ${release.version}</title>
    <content type="xhtml">
    <div xmlns="http://www.w3.org/1999/xhtml">
        <p><a href="${release.changelog_href}">Change log</a></p>
        <p py:for="download in release.downloads">
            <a href="${download}">${download}</a><br />
            <span class="hash">SHA1: <tt>${sha1(download)}</tt></span>
        </p>
    </div>
    </content>
</entry>

</feed>
''')

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser('usage: %prog [options] GIT_DIR', description=__doc__)
    parser.add_option('-f', '--format', type='choice', choices=['html', 'atom'],
            help='Output format [default: %default]')
    parser.set_defaults(format='html')
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('Specify Beaker git dir')

    releases = git_tags.releases(args[0])
    if options.format == 'html':
        stream = html_template.generate(**globals())
        sys.stdout.write(stream.render('xhtml', doctype='html5'))
    elif options.format == 'atom':
        stream = atom_template.generate(**globals())
        sys.stdout.write(stream.render('xml'))
    else:
        assert False
