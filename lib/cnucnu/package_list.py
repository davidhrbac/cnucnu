#!/usr/bin/python
# vim: fileencoding=utf8 foldmethod=marker
#{{{ License header: GPLv2+
#    This file is part of cnucnu.
#
#    Cnucnu is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    Cnucnu is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with cnucnu.  If not, see <http://www.gnu.org/licenses/>.
#}}}

import sys
import re
sys.path.insert(0, './lib')
sys.path.insert(0, '../lib')
sys.path.insert(0, '../../lib')

import cnucnu.errors as cc_errors
from cnucnu.helper import rpm_cmp

class Package(object):

    def __init__(self, name, regex, url, repo):
        # :TODO: add some sanity checks
        self.name = name

        self.regex = regex
        self.url = url
        
        self._latest_upstream = None
        self._upstream_versions = None
        self._repo_version = None
        self._rpm_diff = None

        self.repo = repo
        self.repoid = repo.repoid

    def _invalidate_caches(self):
        self._latest_upstream = None
        self._upstream_versions = None
        self._rpm_diff = None

    def __str__(self):
        return "%(name)s: repo=%(repo_version)s upstream=%(latest_upstream)s" % self

    def __repr__(self):
        return "%(name)s %(regex)s %(url)s" % self

    def __getitem__(self, key):
        return getattr(self, key)

    def set_regex(self, regex):
        if regex == "DEFAULT":
            regex = "%s-([0-9.]*)\\.[tz][ai][rp]" % re.escape(self.name)
        elif regex == "FM-DEFAULT":
            regex = '<a href="/projects/[^/]*/releases/[0-9]*">([^<]*)</a>'
        self.__regex = regex
        self._invalidate_caches()

    regex = property(lambda self:self.__regex, set_regex)
    
    def set_url(self, url):
        if url == "SF-DEFAULT":
            url = "http://prdownloads.sourceforge.net/%s" % self.name
        elif url == "FM-DEFAULT":
            url = "http://freshmeat.net/projects/%s" % self.name

        self.__url = url
        self._invalidate_caches()

    url = property(lambda self:self.__url, set_url)
  
    @property
    def upstream_versions(self):
        if not self._upstream_versions:
            from cnucnu.helper import get_html
            
            try:
                html = get_html(self.url)
            except IOError, ioe:
                raise cc_errors.UpstreamVersionRetrievalError("%(name)s: IO error while retrieving upstream URL. - %(url)s - %(regex)s" % self)

            upstream_versions = re.findall(self.regex, html)
            for version in upstream_versions:
                if " " in version:
                    raise cc_errors.UpstreamVersionRetrievalError("%s: invalid upstream version:>%s< - %s - %s " % (self.name, version, self.url, self.regex))
            if len(upstream_versions) == 0:
                raise cc_errors.UpstreamVersionRetrievalError("%(name)s: no upstream version found. - %(url)s - %(regex)s" % self)

            self._upstream_versions = upstream_versions

            # invalidate sub caches
            self._latest_upstream = None
            self._rpm_diff = None

        return self._upstream_versions

    @property
    def latest_upstream(self):
        if not self._latest_upstream:
            from cnucnu.helper import rpm_max
            self._latest_upstream = rpm_max(self.upstream_versions)
            
            # invalidate _rpm_diff cache
            self._rpm_diff = None

        return self._latest_upstream

    @property
    def repo_version(self):
        if not self._repo_version:
            self._repo_version  = self.repo.package_version(self)
        return self._repo_version

    @property
    def rpm_diff(self):
        if not self._rpm_diff:
            self._rpm_diff = rpm_cmp(self.repo_version, self.latest_upstream)
        return self._rpm_diff

    @property
    def upstream_newer(self):
        return self.rpm_diff == -1
    
    @property
    def repo_newer(self):
        return self.rpm_diff == 1


class Repository:
    def __init__(self, package_list=None, repoid="rawhide-source"):
        self.repoid = repoid
        self.package_list = package_list
        self._package_version_list = None

    def package_version_list(self, package=None):
        if not self._package_version_list or package and package not in self._package_version_list:
            if package and package not in self.package_list:
                self.package_list.packages.append(package)
            package_names = [p.name for p in self.package_list.packages]
            import subprocess as sp
            cmdline = ["/usr/bin/repoquery", "--archlist=src", "--all", "--repoid=rawhide-source", "--qf", "%{name}\t%{version}"]
            cmdline.extend(package_names)

            repoquery = sp.Popen(cmdline, stdout=sp.PIPE)
            (list, stderr) = repoquery.communicate()

            self._package_version_list = dict([e.split("\t") for e in list.split("\n") if e != ""])

        return self._package_version_list

    def package_version(self, package):
        return self.package_version_list(package)[package.name]


class PackageList:
    def __init__(self, repo=Repository()):
        import cnucnu.wiki as wiki
        w = wiki.Wiki()
        page_text = w.get_pagesource("Using_FEver_to_track_upstream_changes")

        import re
        package_line = re.compile(' \\* ([^ ]*) (.*) ([^ \n]*)\n')

        match = package_line.findall(page_text)

        packages = []
        repo.package_list = self
        
        for package in match:
            (name, regex, url) = package
            packages.append(Package(name, regex, url, repo))

        self.packages = packages

    def __getitem__(self, key):
        return self.packages[key]
