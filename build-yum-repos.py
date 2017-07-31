#!/usr/bin/python

"""
Script for generating yum repos for Beaker

This script will pull down the latest Beaker and related packages from 
Brew/Koji, and spit out a hierarchy of directories containing the 
various yum repos for Beaker.
"""

import sys
import os, os.path
import glob
import errno
import re
import shutil
import glob
import urlparse
import requests
import time
import tempfile
import rfc822
from ConfigParser import SafeConfigParser
import koji
import xmlrpclib
import createrepo # needs createrepo >= 0.9

# This is the GPG key id of the Beaker signing key,
# as it is known to Koji (8 characters lower case).
GPG_KEY_ID = '4df16b33'

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    assert os.path.isdir(path), '%s must be a directory' % path

def fetch(url, dest):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    dirname, basename = os.path.split(dest)
    fd, temp_path = tempfile.mkstemp(prefix='.' + basename, dir=dirname)
    f = os.fdopen(fd, 'w')
    try:
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
        f.flush()
        mtime = time.mktime(rfc822.parsedate(response.headers['Last-Modified']))
        os.utime(temp_path, (mtime, mtime))
        os.chmod(temp_path, 0644)
        os.rename(temp_path, dest)
    except:
        os.unlink(temp_path)
        raise

class TargetRepo(object):
    """
    Represents a yum repo to be built.
    Call add_package() to specify which packages should be included,
    then call build() to do it.
    """

    def __init__(self, name, distro, tag, arches, downgradeable, all_packages, signed, hub_url, topurl):
        self.name = name
        self.distro = distro
        self.tag = tag
        self.arches = arches
        self.downgradeable = downgradeable
        self.all_packages = all_packages
        self.signed = signed
        self.hub_url = hub_url
        self.topurl = topurl
        self.package_names = set()
        self.package_tags = {}
        self.excluded_rpms = set()
        self.rpm_names = set()
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

    def add_excluded_rpm(self, rpm_name):
        self.excluded_rpms.add(rpm_name)

    def build(self, dest):
        self.basedir = dest
        if os.path.islink(self.output_dir):
            raise RuntimeError(
                    'Attempted to build yum repo into symlink %s\n'
                    'Hint: delete the symlink first' % self.output_dir)
        self._mirror_all_rpms()
        self._create_repo_metadata()
        self._clean_unused_rpms()

    def _mirror_all_rpms(self):
        print 'Mirroring RPMs for %r' % self
        ensure_dir(self.output_dir)
        koji_session = koji.ClientSession(self.hub_url)
        koji_session.multicall = True
        if self.all_packages:
            if self.downgradeable:
                koji_session.listTaggedRPMS(self.tag, inherit=True)
            else:
                koji_session.getLatestRPMS(self.tag)
        package_names = list(self.package_names)
        for package_name in package_names:
            if self.downgradeable:
                koji_session.listTaggedRPMS(
                        self.package_tags.get(package_name, self.tag),
                        inherit=True, package=package_name)
            else:
                koji_session.getLatestRPMS(
                        self.package_tags.get(package_name, self.tag),
                        package_name)
        results = koji_session.multiCall()
        if self.all_packages:
            result = results.pop(0)
            if 'faultCode' in result:
                raise xmlrpclib.Fault(result['faultCode'], result['faultString'])
            if not result:
                raise ValueError('No packages in tag %s' % self.tag)
            for rpms, builds in result:
                self.rpm_names.update(rpm['name'] for rpm in rpms
                        if rpm['name'] not in self.excluded_rpms)
                self._mirror_rpms_for_build(builds, rpms)
        for i, result in enumerate(results):
            if 'faultCode' in result:
                raise xmlrpclib.Fault(result['faultCode'], result['faultString'])
            if not result or not result[0] or not result[0][1]:
                raise ValueError('Package %s not in tag %s' % (package_names[i],
                        self.package_tags.get(package_names[i], self.tag)))
            (rpms, builds), = result
            self._mirror_rpms_for_build(builds, rpms)

    def _mirror_rpms_for_build(self, builds, rpms):
        pathinfo = koji.PathInfo(self.topurl)
        builds = dict((build['build_id'], build) for build in builds)
        for rpm in rpms:
            if rpm['arch'] not in self.arches + ['noarch', 'src']:
                continue
            if rpm['name'] not in self.rpm_names and rpm['arch'] != 'src':
                continue
            filename = os.path.join(self.output_dir,
                    os.path.basename(pathinfo.rpm(rpm)))
            if self.signed:
                # For signed RPMs, the actual file we want to download is 
                # always *bigger* than the size indicated in Koji. Koji only 
                # tracks the original size of the RPM before signing.
                if os.path.exists(filename) and os.path.getsize(filename) > rpm['size']:
                    print 'Skipping %s' % filename
                else:
                    url = os.path.join(pathinfo.build(builds[rpm['build_id']]),
                            pathinfo.signed(rpm, GPG_KEY_ID))
                    print 'Fetching %s' % url
                    fetch(url, filename)
            else:
                # For unsigned RPMs we can check the exact size here.
                if os.path.exists(filename) and os.path.getsize(filename) == rpm['size']:
                    print 'Skipping %s' % filename
                else:
                    url = os.path.join(pathinfo.build(builds[rpm['build_id']]),
                            pathinfo.rpm(rpm))
                    print 'Fetching %s' % url
                    fetch(url, filename)
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
                        dest_filename = os.path.join(self.output_dir, filename)
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
        conf.pkglist = self.rpm_filenames
        # not sure what this is, but it defaults to True in newer createrepo,
        # but it makes yum explode
        conf.collapse_glibc_requires = False
        mdgen = createrepo.MetaDataGenerator(config_obj=conf)
        mdgen.doPkgMetadata()
        mdgen.doRepoMetadata()
        mdgen.doFinalMove()

    def _clean_unused_rpms(self):
        for filename in glob.iglob(os.path.join(self.output_dir, '*.rpm')):
            if os.path.basename(filename) not in self.rpm_filenames:
                print 'Removing %s' % filename
                os.unlink(filename)

def target_repos_from_config(*config_filenames):
    # We need the hub and package URLs for Koji and Brew.
    # We can load those from the relevant config files.
    koji_config = SafeConfigParser()
    koji_config.read(['/etc/brewkoji.conf', '/etc/koji.conf'] +
            glob.glob('/etc/koji.conf.d/*.conf') +
            [os.path.expanduser('~/.koji/config')])

    config = SafeConfigParser()
    config.optionxform = str # package names are case sensitive
    for filename in config_filenames:
        print 'reading %s' % filename
        config.readfp(open(filename, 'r'))

    repos = {}
    testing_repos = {}
    skipped = set()
    for section in sorted(config.sections()):
        descr, _, rest = section.partition('.')
        if not rest:
            hub_url = koji_config.get(config.get(section, 'source'), 'server')
            topurl = koji_config.get(config.get(section, 'source'), 'topurl')
            downgradeable = True
            if config.has_option(section, 'downgradeable'):
                downgradeable = config.getboolean(section, 'downgradeable')
            all_packages = False
            if config.has_option(section, 'all-packages'):
                all_packages = config.getboolean(section, 'all-packages')
            signed = False
            if config.has_option(section, 'signed'):
                signed = config.getboolean(section, 'signed')
            repos[descr] = TargetRepo(name=config.get(section, 'name'),
                    distro=config.get(section, 'distro'),
                    arches=config.get(section, 'arches').split(),
                    tag=config.get(section, 'tag'),
                    downgradeable=downgradeable,
                    all_packages=all_packages,
                    signed=signed,
                    hub_url=hub_url, topurl=topurl)
            testing_repos[descr] = TargetRepo(name=config.get(section, 'testing-name'),
                    distro=config.get(section, 'distro'),
                    arches=config.get(section, 'arches').split(),
                    tag=config.get(section, 'testing-tag'),
                    downgradeable=downgradeable,
                    all_packages=all_packages,
                    signed=False, # testing repos are always unsigned for now
                    hub_url=hub_url, topurl=topurl)
            if config.has_option(section, 'skip') and config.getboolean(section, 'skip'):
                skipped.add(descr)
            if config.has_option(section, 'excluded-rpms'):
                for name in config.get(section, 'excluded-rpms').split():
                    repos[descr].add_excluded_rpm(name)
                    testing_repos[descr].add_excluded_rpm(name)
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
                testing_tag = tag + '-candidate' if not tag.endswith('-candidate') else tag
                testing_repos[descr].add_package(package_name, rpm_names.split(), testing_tag)
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
