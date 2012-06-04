#!/usr/bin/python -B
# vim: set fileencoding=utf8 :

"""
Takes Beaker's spec file on stdin and writes out the Releases page to stdout, 
based on the contents of the %changelog section.
"""

import sys
import re
from genshi import Markup
from genshi.template import MarkupTemplate

import changelog

def linkify_bugzilla(change):
    def result():
        chunks = re.split(r'(\d{6,})', change)
        while True:
            if not chunks:
                break
            yield chunks.pop(0)
            if not chunks:
                break
            bug_id = chunks.pop(0)
            yield Markup('<a href="https://bugzilla.redhat.com/show_bug.cgi?id=%s">%s</a>'
                    % (bug_id, bug_id))
    return Markup('').join(list(result()))

def strip_change_author(change):
    return re.sub(r'\s*\(\S+@\S+\)\s*$', '', change)

_sha1sums = dict((line[42:].rstrip('\n'), line[:40]) for line in open('releases/SHA1SUM'))
def sha1(filename):
    return _sha1sums[filename]

template = MarkupTemplate('''
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
    h2 {
        display: inline-block;
        margin: 0 0 0.25em 0;
        font-size: 1em;
    }
    .date:before {
        content: "&#183;";
        margin-right: 0.3em;
    }
    .date {
        display: inline-block;
        margin-left: 0.5em;
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
    .changelog {
        margin: 0;
    }
  </style>
</head>
<body>
<div class="header">
  <div class="body_element">
    <div class="title">
      <img src="../images/logo.png" alt="Beaker" />
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

<span py:def="release_descr(release)" py:strip="True">
    Beaker
    <py:if test="release.release != '-1'">hotfix release</py:if>
    ${release.version}<py:if test="release.release != '-1'">${release.release}</py:if>
</span>

<article py:for="release in releases">
    <h2>${release_descr(release)}</h2>
    <div class="date">
        <time datetime="${release.date}" pubdate="pubdate">${release.date.strftime('%-1d %B %Y')}</time>
    </div>
    <div class="downloads">
        <p py:for="download in release.downloads"
           class="download ${'.tar' in download and 'tarball' or ''} ${'.patch' in download and 'patch' or ''}">
            <a href="${download}">${download}</a><br />
            <span class="hash">SHA1: <tt>${sha1(download)}</tt></span>
        </p>
    </div>
    <ul class="changelog">
        <li py:for="change in release.changes">${linkify_bugzilla(strip_change_author(change))}</li>
    </ul>
</article>

<p>For older releases, please refer to
<a href="http://git.beaker-project.org/cgit/beaker/">Beaker’s git repo</a>.</p>

  </div>
</div>
</body>
</html>
''')

if __name__ == '__main__':
    releases = list(changelog.parse(sys.stdin.read().decode('utf8')))
    stream = template.generate(**globals())
    sys.stdout.write(stream.render('xhtml', doctype='html5'))
