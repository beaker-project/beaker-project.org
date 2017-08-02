#!/usr/bin/python

"""
Script for checking dependencies in yum repos for Beaker
"""

import sys
import os, os.path
from ConfigParser import SafeConfigParser
import urlparse
import rpm
import yum

# XXX dodgy
import imp
repoclosure = imp.load_source('repoclosure', '/usr/bin/repoclosure') # from yum-utils

def highest_evr(packages):
    """
    Given an iterable of yum package objects for the same named package, 
    returns the highest Epoch-Version-Release.
    """
    return sorted(((pkg['epoch'], pkg['version'], pkg['release'])
                   for pkg in packages), cmp=rpm.labelCompare, reverse=True)[0]

def check_deps(base, local_repo, repo_urls, arches, build_deps=False,
        ignored_packages=frozenset(), ignored_breakages=frozenset()):
    closure_arches = ['noarch'] + arches
    if build_deps:
        closure_arches.append('src')
    rc = repoclosure.RepoClosure(arch=closure_arches, config='/etc/yum/yum.conf')
    rc.setCacheDir(True)
    rc.repos.disableRepo('*')
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
    only_pkgs = set(pkg.name for pkg in
            rc.repos.getRepo(local_repo_id).getPackageSack().returnNewestByNameArch())
    # Also skip any ignored packages
    only_pkgs.difference_update(ignored_packages)
    rc.pkgonly = list(only_pkgs)
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
        return True
    return False

def check_client_harness_version_match(base, client_repo, harness_repo):
    yb = yum.YumBase()
    yb.doConfigSetup(fn='/etc/yum/yum.conf', init_plugins=False)
    yb.setCacheDir(True)
    yb.repos.disableRepo('*')
    client_repo_url = urlparse.urljoin(base, client_repo)
    client_repo_id = client_repo_url.replace('/', '-')
    yb.add_enable_repo(client_repo_id, baseurls=[client_repo_url])
    harness_repo_url = urlparse.urljoin(base, harness_repo)
    harness_repo_id = harness_repo_url.replace('/', '-')
    yb.add_enable_repo(harness_repo_id, baseurls=[harness_repo_url])
    for name in ['rhts-python', 'beakerlib', 'beakerlib-redhat']:
        client_pkgs = yb.pkgSack.returnPackages(repoid=client_repo_id, patterns=[name])
        harness_pkgs = yb.pkgSack.returnPackages(repoid=harness_repo_id, patterns=[name])
        if not client_pkgs and not harness_pkgs:
            # Doesn't exist at all in the repos, that's fine
            continue
        if highest_evr(client_pkgs) != highest_evr(harness_pkgs):
            print 'Mismatched %s versions across %s:' % (name, client_repo)
            for pkg in client_pkgs:
                print '    ' + str(pkg)
            print '... and %s:' % harness_repo
            for pkg in harness_pkgs:
                print '    ' + str(pkg)
            return True
    return False

def checks_from_config(base, config):
    failed = False

    # Convert base to absolute URL
    if not urlparse.urlparse(base).scheme:
        base = 'file://' + os.path.abspath(base)
    if not base.endswith('/'):
        base += '/' # it's supposed to be a dir

    for section in config.sections():
        local_repo, _, descr = section.partition('.')
        print 'Checking dependencies for %s' % section
        repos = config.get(section, 'repos').split()
        arches = config.get(section, 'arches').split()
        build_deps = False
        if config.has_option(section, 'build-deps'):
            build_deps = config.getboolean(section, 'build-deps')
        ignored_packages = frozenset()
        if config.has_option(section, 'ignored-packages'):
            ignored_packages = frozenset(config.get(section, 'ignored-packages').split())
        ignored_breakages = frozenset()
        if config.has_option(section, 'ignored-breakages'):
            ignored_breakages = frozenset(config.get(section, 'ignored-breakages').split())
        failed |= check_deps(base, local_repo, repos, arches, build_deps,
                ignored_packages, ignored_breakages)

    # This is a particular edge case which we check for specifically, because 
    # it's not covered by the general repoclosure check above. We need to 
    # ensure that the highest version of rhts matches across client and harness 
    # repos, otherwise users who have both client and harness configured on 
    # their system will have upgrade failures like this:
    # http://post-office.corp.redhat.com/archives/beaker-user-list/2015-December/msg00044.html
    # Similarly for beakerlib and beakerlib-redhat:
    # http://post-office.corp.redhat.com/archives/beaker-dev-list/2017-July/msg00009.html
    client_distros = set()
    for section in config.sections():
        local_repo, _, descr = section.partition('.')
        repotype, _, distro = local_repo.partition('/')
        if repotype == 'client':
            client_distros.add(distro)
    for client_distro in client_distros:
        # For every client repo we have, there should be a matching harness repo
        client_repo = 'client/%s' % client_distro
        harness_repo = 'harness/%s' % client_distro
        print 'Checking for version mismatches across %s and %s' % (client_repo, harness_repo)
        failed |= check_client_harness_version_match(base, client_repo, harness_repo)

    if failed:
        sys.exit(1)

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
