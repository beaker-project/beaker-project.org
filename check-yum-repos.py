#!/usr/bin/python

"""
Script for checking dependencies in yum repos for Beaker
"""

import sys
import os, os.path
from ConfigParser import SafeConfigParser

# XXX dodgy
import imp
repoclosure = imp.load_source('repoclosure', '/usr/bin/repoclosure') # from yum-utils

def check_deps(base_dir, local_repo, repo_urls, arches):
    rc = repoclosure.RepoClosure(arch=['noarch'] + arches, config='/etc/yum/yum.conf')
    rc.setCacheDir(True)
    rc.repos.disableRepo('*')
    local_repo_id = local_repo.replace('/', '-')
    rc.add_enable_repo(local_repo_id,
            baseurls=['file://' + os.path.abspath(os.path.join(base_dir, local_repo))])
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
    if broken_deps:
        print '%r failed dependency check using repos:' % local_repo
        for repo_url in repo_urls:
            print '    %s' % repo_url
        for pkg, broken in broken_deps.iteritems():
            print str(pkg)
            for breakage in broken:
                print '    ' + repr(breakage)
        sys.exit(1)

def checks_from_config(base_dir, config):
    for section in config.sections():
        local_repo, _, descr = section.partition('.')
        if not os.path.exists(os.path.join(base_dir, local_repo)):
            print 'Skipping nonexistent %s' % local_repo
            continue
        print 'Checking dependencies for %s' % section
        check_deps(base_dir, local_repo,
                config.get(section, 'repos').split(),
                config.get(section, 'arches').split())

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser('usage: %prog [options]',
            description='Checks dependencies for Beaker repos according to a config file.')
    parser.add_option('-d', '--base-dir', metavar='DIR',
            help='look for repos under DIR [default: %default]')
    parser.add_option('-c', '--config', metavar='FILE', action='append', dest='config_filenames',
            help='load configuration from FILE')
    parser.set_defaults(base_dir='yum', config_filenames=['repoclosure.conf'])

    options, args = parser.parse_args()
    if args:
        parser.error('This program does not accept positional args')

    config = SafeConfigParser()
    config.read(options.config_filenames)
    checks_from_config(options.base_dir, config)
