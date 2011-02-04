#!/usr/bin/python
# vim: fileencoding=utf8 foldmethod=marker
# {{{ License header: GPLv2+
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
# }}}
""" :author: Till Maas
    :contact: opensource@till.name
    :license: GPLv2+
"""
__docformat__ = "restructuredtext"

# python default modules
import re
import urllib

# cnucnu modules
from bugzilla_reporter import BugzillaReporter
from config import global_config
from cvs import CVS
import errors as cc_errors
import helper
from helper import cmp_upstream_repo

#extra modules
import pycurl
from fedora.client.pkgdb import PackageDB

class Repository:
    def __init__(self, name="", path=""):
        if not (name and path):
            c = global_config.config["repo"]
            name = c["name"]
            path = c["path"]

        import string
        self.name = name
        self.path = path
        self.repoid = "cnucnu-%s" % "".join(c for c in name if c in string.letters)

        self.repofrompath = "%s,%s" % (self.repoid, self.path)

        self._nvr_dict = None

    @property
    def nvr_dict(self):
        if not self._nvr_dict:
            self._nvr_dict = self.repoquery()
        return self._nvr_dict

    def repoquery(self, package_names=[]):
        import subprocess as sp
        # TODO: get rid of repofrompath message even with --quiet
        cmdline = ["/usr/bin/repoquery", "--quiet", "--archlist=src", "--all", "--repoid", self.repoid, "--qf", "%{name}\t%{version}\t%{release}"]
        if self.repofrompath:
            cmdline.extend(['--repofrompath', self.repofrompath])
        cmdline.extend(package_names)

        repoquery = sp.Popen(cmdline, stdout=sp.PIPE)
        (list, stderr) = repoquery.communicate()
        new_nvr_dict = {}
        for line in list.split("\n"):
            if line != "":
                name, version, release = line.split("\t")
                new_nvr_dict[name] = (version, release)
        return new_nvr_dict

    def package_version(self, package):
        return self.nvr_dict[package.name][0]

    def package_release(self, package):
        return self.nvr_dict[package.name][1]


class Package(object):

    def __init__(self, name, regex, url, repo=Repository(), cvs=CVS(), br=BugzillaReporter(), nagging=True):
        # :TODO: add some sanity checks
        self.name = name

        self.raw_regex = None
        self.raw_url = None
        self.regex = regex
        self.url = url

        self._html = None
        self._latest_upstream = None
        self._upstream_versions = None
        self._repo_version = None
        self._repo_release = None
        self._rpm_diff = None


        self.repo = repo
        self.repo_name = repo.name
        self.cvs = cvs
        self.br = br
        self.nagging = nagging

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
        self.raw_regex = regex

        name = self.name
        # allow name override with e.g. DEFAULT:othername
        if regex:
            name_override = re.match(r"^((?:FM-)?DEFAULT)(?::(.+))$", regex)
            if name_override:
                regex = name_override.group(1)
                name = name_override.group(2)

        # use DEFAULT regex but alter the name
        if regex == "CPAN-DEFAULT":
            # strip "perl-" prefix only if name was not overridden
            if not name_override and name.startswith("perl-"):
                name = name[len("perl-"):]
                regex = "DEFAULT"
        elif regex == "PEAR-DEFAULT":
            # strip "php-pear-" prefix only if name was not overridden
            if not name_override and name.startswith("php-pear-"):
                name = name[len("php-pear-"):].replace("-","_")
                regex = "DEFAULT"
        elif regex == "PECL-DEFAULT":
            # strip "php-pecl-" prefix only if name was not overridden
            if not name_override and name.startswith("php-pecl-"):
                name = name[len("php-pecl-"):].replace("-","_")
                regex = "DEFAULT"

        # no elif here, because the previous regex aliases are only for name altering
        if regex == "DEFAULT":
            regex = \
                r"\b%s[-_]" % re.escape(name)    + \
                r"(?i)"                          + \
                r"(?:(?:src|source)[-_])?"       + \
                r"([^-/_\s]*?"                   + \
                r"\d"                            + \
                r"[^-/_\s]*?)"                   + \
                r"(?:[-_.](?:src|source|orig))?" + \
                r"\.(?:tar|t[bglx]z|tbz2|zip)\b"
        elif regex == "FM-DEFAULT":
            regex = '<a href="/projects/[^/]*/releases/[0-9]*">([^<]*)</a>'
        elif regex == "HACKAGE-DEFAULT" or regex== "DIR-LISTING-DEFAULT":
            regex = 'href="([0-9][0-9.]*)/"'

        self.__regex = regex
        self._invalidate_caches()

    regex = property(lambda self:self.__regex, set_regex)

    def set_url(self, url):
        self.raw_url = url

        name = self.name
        # allow name override with e.g. SF-DEFAULT:othername
        if url:
            name_override = re.match(r"^((?:SF|FM|GNU|CPAN|HACKAGE|DEBIAN|GOOGLE|PEAR|PECL|PYPI|LP|GNOME)-DEFAULT)(?::(.+))$", url)
            if name_override:
                url = name_override.group(1)
                name = name_override.group(2)
        name = urllib.quote(name, safe='')
        if url == "SF-DEFAULT":
            url = "http://sourceforge.net/projects/%s/files/" % name
        elif url == "FM-DEFAULT":
            url = "http://freshmeat.net/projects/%s" % name
        elif url == "GNU-DEFAULT":
            url = "http://ftp.gnu.org/gnu/%s/" % name
        elif url == "CPAN-DEFAULT":
            # strip "perl-" prefix only if name was not overridden
            if not name_override and name.startswith("perl-"):
                name = name[len("perl-"):]
            url = "http://search.cpan.org/dist/%s/" % name
        elif url == "HACKAGE-DEFAULT":
            # strip "ghc-" prefix only if name was not overridden
            if not name_override and name.startswith("ghc-"):
                name = name[len("ghc-"):]
            url = "http://hackage.haskell.org/packages/archive/%s/" % name
        elif url == "DEBIAN-DEFAULT":
            url = "http://ftp.debian.org/debian/pool/main/%s/%s/" % (name[0], name)
        elif url == "GOOGLE-DEFAULT":
            url = "http://code.google.com/p/%s/downloads/list" % name
        elif url == "PYPI-DEFAULT":
            url = "http://pypi.python.org/packages/source/%s/%s" % (name[0], name)
        elif url == "PEAR-DEFAULT":
            # strip "php-pear-" prefix only if name was not overridden
            if not name_override and name.startswith("php-pear-"):
                name = name[len("php-pear-"):].replace("-","_")
            url = "http://pear.php.net/package/%s/download" % name
        elif url == "PECL-DEFAULT":
            # strip "php-pecl-" prefix only if name was not overridden
            if not name_override and name.startswith("php-pecl-"):
                name = name[len("php-pecl-"):].replace("-","_")
            url = "http://pecl.php.net/package/%s/download" % name
        elif url == "LP-DEFAULT":
            url = "https://launchpad.net/%s/+download" % name
        elif url == "GNOME-DEFAULT":
            url = "http://download.gnome.org/sources/%s/^/" % name

        self.__url = url
        self.html = None

    url = property(lambda self:self.__url, set_url)

    def set_html(self, html):
        self._html = html
        self._invalidate_caches()

    def get_html(self):
        if not self._html:
            from cnucnu.helper import get_html, expand_subdirs

            try:
                self.__url = expand_subdirs(self.url)
                html = get_html(self.url)
            # TODO: get_html should raise a generic retrieval error
            except IOError, ioe:
                raise cc_errors.UpstreamVersionRetrievalError("%(name)s: IO error while retrieving upstream URL. - %(url)s - %(regex)s" % self)
            except pycurl.error, e:
                raise cc_errors.UpstreamVersionRetrievalError("%(name)s: Pycurl while retrieving upstream URL. - %(url)s - %(regex)s" % self + " " + str(e))
            self.html = html
        return self._html

    html = property(get_html, set_html)

    @property
    def upstream_versions(self):
        if not self._upstream_versions:

            upstream_versions = re.findall(self.regex, self.html)
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
            from cnucnu.helper import upstream_max
            self._latest_upstream = upstream_max(self.upstream_versions)

            # invalidate _rpm_diff cache
            self._rpm_diff = None

        return self._latest_upstream

    @property
    def repo_version(self):
        if not self._repo_version:
            self._repo_version  = self.repo.package_version(self)
        return self._repo_version

    @property
    def repo_release(self):
        if not self._repo_release:
            self._repo_release  = self.repo.package_release(self)
        return self._repo_release

    @property
    def rpm_diff(self):
        if not self._rpm_diff:
            self._rpm_diff = cmp_upstream_repo(self.latest_upstream, (self.repo_version, self.repo_release))
        return self._rpm_diff

    @property
    def upstream_newer(self):
        return self.rpm_diff == 1

    @property
    def repo_newer(self):
        return self.rpm_diff == -1

    @property
    def status(self):
        if self.upstream_newer:
            return "(outdated)"
        elif self.repo_newer:
            return "(%(repo_name)s newer)" % self
        else:
            return ""

    @property
    def upstream_version_in_cvs(self):
        return self.cvs.has_upstream_version(self)

    @property
    def exact_outdated_bug(self):
        return self.br.get_exact_outdated_bug(self)

    @property
    def open_outdated_bug(self):
        return self.br.get_open_outdated_bug(self)

    def report_outdated(self, dry_run=True):
        if self.nagging:
            if not self.upstream_newer:
                print "Upstream of package not newer, report_outdated aborted!" + str(self)
                return None

#            if self.upstream_version_in_cvs:
#                print "Upstream Version found in CVS, skipping bug report: %(name)s U:%(latest_upstream)s R:%(repo_version)s" % self
#                return None

            return self.br.report_outdated(self, dry_run)
        else:
            print "Nagging disabled for package: %s" % str(self)
            return None



class PackageList:
    def __init__(self, repo=Repository(), cvs=CVS(), br=BugzillaReporter(), mediawiki=False, packages=None):
        """ A list of packages to be checked.

        :Parameters:
            repo : `cnucnu.Repository`
                Repository to compare with upstream
            cvs : `cnucnu.CVS`
                CVS to compares sources files with upstream version
            mediawiki : dict
                Get a list of package names, urls and regexes from a mediawiki page defined in the dict.
            packages : [cnucnu.Package]
                List of packages to populate the package_list with

        """
        if not mediawiki:
            mediawiki = global_config.config["package list"]["mediawiki"]
        if not packages and mediawiki:

            from wiki import MediaWiki
            w = MediaWiki(base_url=mediawiki["base url"])
            page_text = w.get_pagesource(mediawiki["page"])

            ignore_owner_regex = re.compile('\\* ([^ ]*)')
            owners = [o[0].encode("UTF-8") for o in helper.match_interval(page_text, ignore_owner_regex, "== Package Owner Ignore List ==", "<!-- END PACKAGE OWNER IGNORE LIST -->")]

            pdb = PackageDB()
            ignore_packages = []
            for owner in owners:
                pkgs = pdb.user_packages(owner, acls="owner")["pkgs"]
                p_names = [p["name"] for p in pkgs]
                ignore_packages.extend(p_names)
            set(ignore_packages)

            packages = []
            repo.package_list = self
            package_line_regex = re.compile(' \\* ([^ ]*) (.*) ([^ ]*)')
            for package_data in helper.match_interval(page_text, package_line_regex, "== List Of Packages ==", "<!-- END LIST OF PACKAGES -->"):
                (name, regex, url) = package_data
                nagging = True
                if name in ignore_packages:
                    nagging = False
                packages.append(Package(name, regex, url, repo, cvs, br, nagging=nagging))

        self.packages = packages
        self.append = self.packages.append

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.packages[key]
        elif isinstance(key, str):
            for p in self.packages:
                if p.name == key:
                    return p
            raise KeyError("Package %s not found" % key)


if __name__ == '__main__':
    pl = PackageList()
    p = pl.packages[0]
    print p.upstream_versions
