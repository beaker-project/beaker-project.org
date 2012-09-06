#!/usr/bin/python

import sys
import lxml.html

tree = lxml.html.parse(sys.stdin, parser=lxml.html.HTMLParser(encoding='utf8'))
for a in tree.findall('//a[@href="#TOC"]'):
    a.drop_tag()
tree.write(sys.stdout, encoding='utf8', method='html')
