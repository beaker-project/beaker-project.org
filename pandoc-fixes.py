#!/usr/bin/python

import sys
import lxml.html, lxml.html.builder

A = lxml.html.builder.A

tree = lxml.html.parse(sys.stdin, parser=lxml.html.HTMLParser(encoding='utf8'))
for a in tree.findall('//a[@href="#TOC"]'):
    a.drop_tag()
for section in tree.findall('//section'):
    h = section.xpath('.//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6]')[0]
    h.text += ' '
    h.append(A(u'\u00b6', {'class': 'headerlink'}, href='#%s' % section.get('id')))
tree.write(sys.stdout, encoding='utf8', method='html')
