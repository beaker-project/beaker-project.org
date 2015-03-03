#!/usr/bin/python

"""
Script for generating yum repos for Beaker

This script will pull down the latest Beaker and related packages from 
Brew/Koji, and spit out a hierarchy of directories containing the 
various yum repos for Beaker.
"""

import sys
import os, os.path
import errno
import re
import shutil
import glob
import urlparse
import urllib2
from ConfigParser import SafeConfigParser
import koji
import xmlrpclib
import createrepo # needs createrepo >= 0.9

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    assert os.path.isdir(path), '%s must be a directory' % path

class TargetRepo(object):
    """
    Represents a yum repo to be built.
    Call add_package() to specify which packages should be included,
    then call build() to do it.
    """

    def __init__(self, name, distro, tag, arches, downgradeable, hub_url, topurl):
        self.name = name
        self.distro = distro
        self.tag = tag
        self.arches = arches
        self.downgradeable = downgradeable
        self.hub_url = hub_url
        self.topurl = topurl
        self.package_names = set()
        self.package_tags = {}
        self.rpm_names = set()
        self.buildarch_task_ids = set()
        self.manual_builds = set()
        self.rpm_filenames = set()

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.output_dir)

    @property
    def output_dir(self):
        return os.path.join(self.basedir, self.name, self.distro)

    def add_package(self, package_name, rpm_names=None, tag=None):
        self.package_names.add(package_name)
        self.rpm_names.update(rpm_names or [package_name])
        if tag:
            self.package_tags[package_name] = tag

    def add_scratch_build(self, buildarch_task_id, rpm_names):
        """
        Use this if you need to grab a package built in a Koji scratch build,
        instead of a normal tagged build.
        Pass the id of the buildArch task (not the build task!)
        """
        self.buildarch_task_ids.add(int(buildarch_task_id))
        self.rpm_names.update(rpm_names)

    def add_manual_build(self, rpm_glob, rpm_names):
        """
        Use this if you need to add packages that were built outside of
        koji or brew.
        """
        self.manual_builds.add(rpm_glob)
        self.rpm_names.update(rpm_names)

    def build(self, dest):
        self.basedir = dest
        self._mirror_all_rpms()
        self._create_repo_metadata()

    def _mirror_all_rpms(self):
        print 'Mirroring RPMs for %r' % self
        ensure_dir(os.path.join(self.basedir, 'rpms'))
        koji_session = koji.ClientSession(self.hub_url)
        # normal tagged builds
        package_names = list(self.package_names)
        koji_session.multicall = True
        for package_name in package_names:
            if self.downgradeable:
                koji_session.listTaggedRPMS(
                        self.package_tags.get(package_name, self.tag),
                        inherit=True, package=package_name)
            else:
                koji_session.getLatestRPMS(
                        self.package_tags.get(package_name, self.tag),
                        package_name)
        for i, result in enumerate(koji_session.multiCall()):
            if 'faultCode' in result:
                raise xmlrpclib.Fault(result['faultCode'], result['faultString'])
            if not result or not result[0] or not result[0][1]:
                raise ValueError('Package %s not in tag %s' % (package_names[i],
                        self.package_tags.get(package_names[i], self.tag)))
            (rpms, builds), = result
            self._mirror_rpms_for_build(builds, rpms)
        # scratch builds by task id
        task_ids = list(self.buildarch_task_ids)
        koji_session.multicall = True
        for task_id in task_ids:
            koji_session.listTaskOutput(task_id)
        for task_id, result in zip(task_ids, koji_session.multiCall()):
            if 'faultCode' in result:
                raise xmlrpclib.Fault(result['faultCode'], result['faultString'])
            filenames, = result
            if not filenames:
                raise ValueError('No output files for task %d -- scratch build expired?' % task_id)
            self._mirror_rpms_for_task(koji_session, task_id, filenames)
        # manual builds by file glob
        manual_builds = list(self.manual_builds)
        for manual_build in manual_builds:
            rpms = glob.glob(manual_build)
            if not rpms:
                raise ValueError('No output files for manual glob %s -- mispelled?' % manual_build)
            self._mirror_rpms_for_manual(rpms)

    def _mirror_rpms_for_manual(self, rpms):
        for rpm in rpms:
            filename = os.path.join(self.basedir, 'rpms',
                    os.path.basename(rpm))
            if os.path.exists(filename):
                print 'Skipping %s' % filename
            else:
                print 'Copying %s' % rpm
                shutil.copyfileobj(open(rpm, 'r'), open(filename, 'w'))
            self.rpm_filenames.add(os.path.basename(filename))

    def _mirror_rpms_for_build(self, builds, rpms):
        pathinfo = koji.PathInfo(self.topurl)
        builds = dict((build['build_id'], build) for build in builds)
        for rpm in rpms:
            if rpm['arch'] not in self.arches + ['noarch', 'src']:
                continue
            if rpm['name'] not in self.rpm_names and rpm['arch'] != 'src':
                continue
            filename = os.path.join(self.basedir, 'rpms',
                    os.path.basename(pathinfo.rpm(rpm)))
            if os.path.exists(filename) and os.path.getsize(filename):
                # XXX check md5
                print 'Skipping %s' % filename
            else:
                url = os.path.join(pathinfo.build(builds[rpm['build_id']]),
                        pathinfo.rpm(rpm))
                print 'Fetching %s' % url
                with open(filename, 'w') as dest:
                    src = urllib2.urlopen(url)
                    shutil.copyfileobj(src, dest)
            if not os.path.getsize(filename):
                raise RuntimeError("Failed to download %s" % filename)
            self.rpm_filenames.add(os.path.basename(filename))

    def _mirror_rpms_for_task(self, koji_session, task_id, filenames):
        patterns = [re.compile(r'%s-\d.*\.(\w+)\.rpm' % re.escape(r))
                for r in self.rpm_names]
        for filename in filenames:
            for pattern in patterns:
                m = pattern.match(filename)
                if m:
                    arch = m.group(1)
                    if arch in self.arches + ['noarch', 'src']:
                        dest_filename = os.path.join(self.basedir, 'rpms', filename)
                        if os.path.exists(dest_filename):
                            print 'Skipping %s' % dest_filename
                        else:
                            print 'Fetching %s from task id %s' % (filename, task_id)
                            contents = koji_session.downloadTaskOutput(task_id, filename)
                            dest_file = open(dest_filename, 'w')
                            dest_file.write(contents)
                            dest_file.close()
                        self.rpm_filenames.add(filename)

    def _create_repo_metadata(self):
        print 'Creating repodata for %r' % self
        ensure_dir(self.output_dir)
        conf = createrepo.MetaDataConfig()
        conf.database = False
        conf.outputdir = self.output_dir
        conf.directory = self.output_dir
        conf.directories = [self.output_dir]
        if re.match(r'RedHatEnterpriseLinux[345]$', self.distro):
            conf.sumtype = 'sha'
        conf.pkglist = [os.path.join('..', '..', 'rpms', fn) for fn in self.rpm_filenames]
        # not sure what this is, but it defaults to True in newer createrepo,
        # but it makes yum explode
        conf.collapse_glibc_requires = False
        mdgen = createrepo.MetaDataGenerator(config_obj=conf)
        mdgen.doPkgMetadata()
        mdgen.doRepoMetadata()
        mdgen.doFinalMove()

def clean_unused_rpms(basedir, rpm_filenames):
    rpms_dir = os.path.join(basedir, 'rpms')
    print 'Cleaning unused RPMs from %s' % rpms_dir
    for filename in glob.iglob(os.path.join(basedir, 'rpms', '*.rpm')):
        if os.path.basename(filename) not in rpm_filenames:
            print 'Removing %s' % filename
            os.unlink(filename)

def target_repos_from_config(*config_filenames):
    # We need the hub and package URLs for Koji and Brew.
    # We can load those from the relevant config files.
    koji_config = SafeConfigParser()
    koji_config.read(['/etc/brewkoji.conf', '/etc/koji.conf',
            os.path.expanduser('~/.koji/config')])

    config = SafeConfigParser()
    config.optionxform = str # package names are case sensitive
    for filename in config_filenames:
        print 'reading %s' % filename
        config.readfp(open(filename, 'r'))

    repos = {}
    testing_repos = {}
    skipped = set()
    for section in sorted(config.sections()):
        if section == 'scratch_build_ids':
            continue # skip it
        descr, _, rest = section.partition('.')
        if not rest:
            hub_url = koji_config.get(config.get(section, 'source'), 'server')
            topurl = koji_config.get(config.get(section, 'source'), 'topurl')
            downgradeable = True
            if config.has_option(section, 'downgradeable'):
                downgradeable = config.getboolean(section, 'downgradeable')
            repos[descr] = TargetRepo(name=config.get(section, 'name'),
                    distro=config.get(section, 'distro'),
                    arches=config.get(section, 'arches').split(),
                    tag=config.get(section, 'tag'),
                    downgradeable=downgradeable,
                    hub_url=hub_url, topurl=topurl)
            testing_repos[descr] = TargetRepo(name=config.get(section, 'testing-name'),
                    distro=config.get(section, 'distro'),
                    arches=config.get(section, 'arches').split(),
                    tag=config.get(section, 'testing-tag'),
                    downgradeable=downgradeable,
                    hub_url=hub_url, topurl=topurl)
            if config.has_option(section, 'skip') and config.getboolean(section, 'skip'):
                skipped.add(descr)
        elif rest == 'packages':
            for package_name, rpm_names in config.items(section):
                repos[descr].add_package(package_name, rpm_names.split())
                testing_repos[descr].add_package(package_name, rpm_names.split())
        elif rest.startswith('packages.'):
            tag = rest[len('packages.'):]
            for package_name, rpm_names in config.items(section):
                repos[descr].add_package(package_name, rpm_names.split(), tag)
                # appending -candidate here is perhaps an unwise hack...
                # we just need to work towards eliminating these exceptional sections
                testing_repos[descr].add_package(package_name, rpm_names.split(), tag + '-candidate')
        elif rest == 'scratch-builds':
            for identifier, rpm_names in config.items(section):
                scratch_build_ids = config.get('scratch_build_ids', identifier).split()
                for scratch_build_id in scratch_build_ids:
                    repos[descr].add_scratch_build(scratch_build_id, rpm_names.split() or [identifier])
                    testing_repos[descr].add_scratch_build(scratch_build_id, rpm_names.split() or [identifier])
        elif rest == 'manual-builds':
            for glob, rpm_names in config.items(section):
                repos[descr].add_manual_build(glob, rpm_names.split())
                testing_repos[descr].add_manual_build(glob, rpm_names.split())
        else:
            raise ValueError('Unrecognised section: %s' % rest)
    for descr in skipped:
        del repos[descr]
        del testing_repos[descr]
    return sorted(repos.values() + testing_repos.values())

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser('usage: %prog [options]',
            description='Builds a hierarchy of Beaker repos according to a config file.')
    parser.add_option('-d', '--dest', metavar='DIR',
            help='build repos under DIR [default: %default]')
    parser.add_option('-c', '--config', metavar='FILE', action='append', dest='config_filenames',
            help='load repo configuration from FILE')
    parser.add_option('--repo', metavar='REPO', action='append', dest='repos',
            help='only build REPO [default: all repos]')
    parser.add_option('--distro', metavar='DISTRO', action='append', dest='distros',
            help='only build repos for DISTRO [default: all distros]')
    parser.set_defaults(dest='./yum')

    options, args = parser.parse_args()
    if args:
        parser.error('This program does not accept positional args')

    target_repos = target_repos_from_config(*options.config_filenames or ['yum-repos.conf'])

    if options.repos:
        for name in options.repos:
            if not any(t.name == name for t in target_repos):
                parser.error('Repo with name %s is not defined' % name)
        for t in list(target_repos):
            if t.name not in options.repos:
                target_repos.remove(t)
    if options.distros:
        for distro in options.distros:
            if not any(t.distro == distro for t in target_repos):
                parser.error('Distro %s is not defined for any repos' % distro)
        for t in list(target_repos):
            if t.distro not in options.distros:
                target_repos.remove(t)

    for t in target_repos:
        t.build(options.dest)

    # Clean up, but only if we haven't skipped anything
    if not options.repos and not options.distros:
        used_rpm_filenames = set()
        for t in target_repos:
            used_rpm_filenames.update(t.rpm_filenames)
        clean_unused_rpms(options.dest, used_rpm_filenames)

