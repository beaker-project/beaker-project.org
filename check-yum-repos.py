#!/usr/bin/python

"""
Script for checking dependencies in yum repos for Beaker
"""

import sys
import os, os.path
from ConfigParser import SafeConfigParser
import urlparse

# XXX dodgy
import imp
repoclosure = imp.load_source('repoclosure', '/usr/bin/repoclosure') # from yum-utils

def check_deps(base, local_repo, repo_urls, arches, build_deps=False,
        ignored_breakages=frozenset()):
    closure_arches = ['noarch'] + arches
    if build_deps:
        closure_arches.append('src')
    rc = repoclosure.RepoClosure(arch=closure_arches, config='/etc/yum/yum.conf')
    rc.setCacheDir(True)
    rc.repos.disableRepo('*')
    if not urlparse.urlparse(base).scheme:
        base = 'file://' + os.path.abspath(base)
    if not base.endswith('/'):
        base += '/' # it's supposed to be a dir
    local_repo_url = urlparse.urljoin(base, local_repo)
    local_repo_id = local_repo_url.replace('/', '-')
    rc.add_enable_repo(local_repo_id, baseurls=[local_repo_url])
    # Expand $arch in repo URLs
    for repo_url in list(repo_urls):
        if '$arch' in repo_url:
            repo_urls.remove(repo_url)
            for arch in arches:
                if arch == 'i686':
                    arch = 'i386' # packages are i686 but it's called i386 in the URL
                repo_urls.append(repo_url.replace('$arch', arch))
    for repo_url in repo_urls:
        rc.add_enable_repo(repo_url.replace('/', '-'), baseurls=[repo_url])
    rc.readMetadata()
    # Only check deps for our local repo, not the entire distro
    rc.pkgonly = list(set(pkg.name for pkg in
            rc.repos.getRepo(local_repo_id).getPackageSack().returnNewestByNameArch()))
    broken_deps = rc.getBrokenDeps()

    for pkg in broken_deps:
        broken_deps[pkg] = [breakage for breakage in broken_deps[pkg]
                if breakage[0] not in ignored_breakages]
    broken_deps = dict((pkg, broken) for pkg, broken in broken_deps.iteritems() if broken)

    if broken_deps:
        print '%r failed dependency check using repos:' % local_repo
        for repo_url in repo_urls:
            print '    %s' % repo_url
        for pkg, broken in broken_deps.iteritems():
            print str(pkg)
            for breakage in broken:
                print '    ' + repr(breakage)
        sys.exit(1)

def checks_from_config(base, config):
    for section in config.sections():
        local_repo, _, descr = section.partition('.')
        print 'Checking dependencies for %s' % section
        repos = config.get(section, 'repos').split()
        arches = config.get(section, 'arches').split()
        build_deps = False
        if config.has_option(section, 'build-deps'):
            build_deps = config.getboolean(section, 'build-deps')
        ignored_breakages = frozenset()
        if config.has_option(section, 'ignored-breakages'):
            ignored_breakages = frozenset(config.get(section, 'ignored-breakages').split())
        check_deps(base, local_repo, repos, arches, build_deps, ignored_breakages)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser('usage: %prog [options]',
            description='Checks dependencies for Beaker repos according to a config file.')
    parser.add_option('-d', '--base', metavar='LOCATION',
            help='look for repos under LOCATION (either directory or absolute URL) [default: %default]')
    parser.add_option('-c', '--config', metavar='FILE', action='append', dest='config_filenames',
            help='load configuration from FILE')
    parser.set_defaults(base='yum', config_filenames=['repoclosure.conf'])

    options, args = parser.parse_args()
    if args:
        parser.error('This program does not accept positional args')

    config = SafeConfigParser()
    config.read(options.config_filenames)
    checks_from_config(options.base, config)
