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
from scm import SCM
import errors as cc_errors
import helper
from helper import cmp_upstream_repo

#extra modules
import pycurl
from fedora.client.pkgdb import PackageDB

class Repository:
    def __init__(self, name="", path=""):
        #print "Repository HERE"
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
        #cmdline = ["/usr/bin/repoquery", "--quiet", "--archlist=src", "--all", "--repoid", self.repoid, "--qf", "%{name}\t%{version}\t%{release}\n"]
        cmdline = ["/usr/bin/repoquery", "--archlist=src", "--all", "--repoid", self.repoid, "--qf", "%{name}\t%{version}\t%{release}\n"]
        if self.repofrompath:
            cmdline.extend(['--repofrompath', self.repofrompath])
        cmdline.extend(package_names)
        #print "Packages_names:",package_names
        #print "cmdline Here:",cmdline
        #repoquery = sp.Popen(cmdline, close_fds=True, stdout=sp.PIPE)
        repoquery = sp.Popen(cmdline, stdout=sp.PIPE)
        (list2, stderr) = repoquery.communicate()
        new_nvr_dict = {}
#        list = """razor-agents\t1.34\t1.rf
##postgresql-relay\t1.3\t2.2.rf"""
        #print "stderr:",stderr
        #print "type:",type(list2)
        #print "type:",type(list2.split("\n"))
        for d in list2.split("\n"):
            if d !="":
                if len(d.split("\t"))>=3:
                    #print d
                    name, version, release = d.split("\t")
                    new_nvr_dict[name] = (version, release)
            #    print len(na)

        #for line in list2.split("\n"):
        #    if line != "":
        #        name, version, release = line.split("\t")
        #        new_nvr_dict[name] = (version, release)
        #        print "Name:", name, version, release

        return new_nvr_dict

    def package_version(self, package):
        return self.nvr_dict[package.name][0]

    def package_release(self, package):
        return self.nvr_dict[package.name][1]


class Package(object):

    def __init__(self, name, regex, url, repo=Repository(), scm=SCM(), br=BugzillaReporter(), nagging=True):
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
        self.scm = scm
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
            url = "http://sourceforge.net/api/file/index/project-name/%s/mtime/desc/limit/40/rss" % name
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
            url = "http://download.gnome.org/sources/%s/*/" % name
        
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
            print "HRB33" 
            print self.regex 
            print "HRB33" 
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

            #print "self.upstream_versions", self.upstream_versions
            #print "self._latest_upstream", self._latest_upstream
            # invalidate _rpm_diff cache
            self._rpm_diff = None

        return self._latest_upstream

    @property
    def repo_version(self):
        #print "self._repo_version", self._repo_version
        if not self._repo_version:
            self._repo_version  = self.repo.package_version(self)
        return self._repo_version

    @property
    def repo_release(self):
        if not self._repo_release:
            self._repo_release  = self.repo.package_release(self)
        #print self._repo_release
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
    def upstream_version_in_scm(self):
        return self.scm.has_upstream_version(self)

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

            if self.upstream_version_in_scm:
                print "\tUpstream Version found in SCM, skipping bug report: %(name)s U:%(latest_upstream)s R:%(repo_version)s" % self
                return 

            #return self.br.report_outdated(self, dry_run)
            return None
        else:
            print "Nagging disabled for package: %s" % str(self)
            return None



class PackageList:
    def __init__(self, repo=Repository(), scm=SCM(), br=BugzillaReporter(), mediawiki=False, packages=None):
        """ A list of packages to be checked.

        :Parameters:
            repo : `cnucnu.Repository`
                Repository to compare with upstream
            scm : `cnucnu.SCM`
                SCM to compares sources files with upstream version
            mediawiki : dict
                Get a list of package names, urls and regexes from a mediawiki page defined in the dict.
            packages : [cnucnu.Package]
                List of packages to populate the package_list with

        """
#        if not mediawiki:
#            mediawiki = global_config.config["package list"]["mediawiki"]
#            print "EEE"
        if not packages and mediawiki:

#           from wiki import MediaWiki
#           w = MediaWiki(base_url=mediawiki["base url"])
#           page_text = w.get_pagesource(mediawiki["page"])
#
#           ignore_owner_regex = re.compile('\\* ([^ ]*)')
#           owners = [o[0].encode("UTF-8") for o in helper.match_interval(page_text, ignore_owner_regex, "== Package Owner Ignore List ==", "<!-- END PACKAGE OWNER IGNORE LIST -->")]
#
            pdb = PackageDB()
            ignore_packages = []
#           for owner in owners:
#               pkgs = pdb.user_packages(owner, acls="owner")["pkgs"]
#               p_names = [p["name"] for p in pkgs]
#               ignore_packages.extend(p_names)
#           set(ignore_packages)

            packages = []
            repo.package_list = self
            package_line_regex = re.compile(' \\* ([^ ]*) (.*) ([^ ]*)')
            page_text = """
== List Of Packages ==
 * altermime DEFAULT http://www.pldaniels.com/altermime/
 * amavisd-new amavisd-new-(2\.[0-9.]*?).tar.gz http://www.amavis.org/
 * apcupsd DEFAULT http://sourceforge.net/api/file/index/project-name/apcupsd/mtime/desc/limit/30/rss
 * apt-dater DEFAULT SF-DEFAULT
 * arc DEFAULT SF-DEFAULT
 * arj DEFAULT SF-DEFAULT
 * augeas DEFAULT http://augeas.net/download/
 * awstats DEFAULT SF-DEFAULT
 * bashdb DEFAULT SF-DEFAULT
 * cabextract DEFAULT http://www.cabextract.org.uk/
 * cacti DEFAULT http://www.cacti.net/downloads/
 * cacti-spine DEFAULT http://www.cacti.net/downloads/spine/
 * chkrootkit DEFAULT ftp://ftp.pangeia.com.br/pub/seg/pac/
 * clamav DEFAULT SF-DEFAULT
 * clusterssh DEFAULT SF-DEFAULT
 * crossroads DEFAULT http://crossroads.e-tunity.com/downloads/versions/
 * denyhosts DEFAULT SF-DEFAULT
 * discount DEFAULT http://www.pell.portland.or.us/~orc/Code/discount/
 * dnsmasq DEFAULT http://www.thekelleys.org.uk/dnsmasq/
 * eggdrop eggdrop([0-9.]*?).tar.gz ftp://ftp.eggheads.org/pub/eggdrop/GNU/stable/
 * enma DEFAULT SF-DEFAULT
 * etckeeper DEFAULT http://ftp.debian.org/debian/pool/main/e/etckeeper/
 * fail2ban DEFAULT https://github.com/fail2ban/fail2ban/downloads
 * fdupes fdupes-(.*?).tar.gz GOOGLE-DEFAULT
 * freetds DEFAULT ftp://ftp.ibiblio.org/pub/Linux/ALPHA/freetds/stable/
 * freeze DEFAULT http://www.ibiblio.org/pub/Linux/utils/compress/
 * fuse-rdiff-backup-fs DEFAULT:rdiff-backup-fs GOOGLE-DEFAULT
 * fuse-rdiff-backup-fs DEFAULT:rdiff-backup-fs GOOGLE-DEFAULT:rdiff-backup-fs
 * ganglia DEFAULT SF-DEFAULT
 * gifsicle DEFAULT http://www.lcdf.org/gifsicle/
 * git git-([0-9.]*?).tar.gz GOOGLE-DEFAULT:git-core
 * htop DEFAULT SF-DEFAULT
 * icinga DEFAULT SF-DEFAULT
 * icinga-web DEFAULT http://sourceforge.net/projects/icinga/files/icinga-web/
 * iftop DEFAULT http://www.ex-parrot.com/~pdw/iftop/download/
 * lambdamoo DEFAULT SF-DEFAULT
 * ldns DEFAULT http://www.nlnetlabs.nl/downloads/ldns/
 * lha DEFAULT DEFAULT
 * libspf2 DEFAULT http://www.libspf2.org/spf/
 * libtorrent DEFAULT http://libtorrent.rakshasa.no/downloads/
 * lshw lshw-B.([\d.]*?).tar.gz http://ezix.org/software/files/
 * lzo DEFAULT http://www.oberhumer.com/opensource/lzo/download/
 * lzop DEFAULT http://www.lzop.org/download/
 * mercurial DEFAULT http://mercurial.selenic.com/release/
 * mfs DEFAULT http://www.moosefs.org/download.html
 * milter-greylist DEFAULT http://ftp.espci.fr/pub/milter-greylist/
 * mirmon DEFAULT http://people.cs.uu.nl/henkp/mirmon/
 * mk-configure DEFAULT SF-DEFAULT
 * mod_fastcgi DEFAULT http://www.fastcgi.com/dist/
 * monit DEFAULT http://mmonit.com/monit/dist/
 * monitorix DEFAULT http://www.monitorix.org/
 * nagios DEFAULT SF-DEFAULT
 * nagios-plugins DEFAULT http://sourceforge.net/projects/nagiosplug/files/nagiosplug/
 * netperf DEFAULT ftp://ftp.netperf.org/netperf/
 * nload DEFAULT http://www.roland-riegel.de/nload/
 * nmap nmap-([0-9.]*?).tgz http://nmap.org/dist/
 * nmon DEFAULT SF-DEFAULT
 * nomarch DEFAULT http://www.ibiblio.org/pub/Linux/utils/compress/
 * opendkim opendkim-([\d.]*?).tar.gz SF-DEFAULT
 * openvpn DEFAULT http://swupdate.openvpn.org/community/releases/
 * p7zip p7zip_([\d\.]+)_src_all.tar.bz SF-DEFAULT
 * perl-Apache2-AuthenNIS CPAN-DEFAULT CPAN-DEFAULT
 * perl-Archive-Zip CPAN-DEFAULT CPAN-DEFAULT
 * perl-Array-Columnize CPAN-DEFAULT CPAN-DEFAULT
 * perl-BerkeleyDB CPAN-DEFAULT CPAN-DEFAULT
 * perl-Class-Accessor-Grouped CPAN-DEFAULT CPAN-DEFAULT
 * perl-Compress-Raw-Bzip2 CPAN-DEFAULT CPAN-DEFAULT
 * perl-Compress-Raw-Zlib CPAN-DEFAULT CPAN-DEFAULT
 * perl-Compress-Zlib CPAN-DEFAULT CPAN-DEFAULT
 * perl-Config-Any CPAN-DEFAULT CPAN-DEFAULT
 * perl-Convert-BinHex CPAN-DEFAULT CPAN-DEFAULT
 * perl-Convert-TNEF CPAN-DEFAULT CPAN-DEFAULT
 * perl-Convert-UUlib CPAN-DEFAULT CPAN-DEFAULT
 * perl-Crypt-OpenSSL-RSA CPAN-DEFAULT CPAN-DEFAULT
 * perl-DBD-Sybase CPAN-DEFAULT CPAN-DEFAULT
 * perl-DBI CPAN-DEFAULT CPAN-DEFAULT
 * perl-DB_File CPAN-DEFAULT CPAN-DEFAULT
 * perl-Dancer CPAN-DEFAULT CPAN-DEFAULT
 * perl-Data-Dumper-Concise CPAN-DEFAULT CPAN-DEFAULT
 * perl-Digest-HMAC CPAN-DEFAULT CPAN-DEFAULT
 * perl-Digest-MD5 CPAN-DEFAULT CPAN-DEFAULT
 * perl-Digest-SHA CPAN-DEFAULT CPAN-DEFAULT
 * perl-Digest-SHA1 CPAN-DEFAULT CPAN-DEFAULT
 * perl-Email-Date-Format CPAN-DEFAULT CPAN-DEFAULT
 * perl-Encode-Detect CPAN-DEFAULT CPAN-DEFAULT
 * perl-Error CPAN-DEFAULT CPAN-DEFAULT
 * perl-Geography-Countries CPAN-DEFAULT CPAN-DEFAULT
 * perl-Getopt-Long-Descriptive CPAN-DEFAULT CPAN-DEFAULT
 * perl-HTML-Parser CPAN-DEFAULT CPAN-DEFAULT
 * perl-HTML-Tagset CPAN-DEFAULT CPAN-DEFAULT
 * perl-IO-Compress CPAN-DEFAULT CPAN-DEFAULT
 * perl-IO-Multiplex CPAN-DEFAULT CPAN-DEFAULT
 * perl-IO-Socket-SSL CPAN-DEFAULT CPAN-DEFAULT
 * perl-IO-Zlib CPAN-DEFAULT CPAN-DEFAULT
 * perl-IO-stringy CPAN-DEFAULT CPAN-DEFAULT
 * perl-IP-Country CPAN-DEFAULT CPAN-DEFAULT
 * perl-List-Cycle CPAN-DEFAULT CPAN-DEFAULT
 * perl-MIME-Base64 CPAN-DEFAULT CPAN-DEFAULT
 * perl-MIME-Lite CPAN-DEFAULT CPAN-DEFAULT
 * perl-MIME-tools CPAN-DEFAULT CPAN-DEFAULT
 * perl-Mail-DKIM CPAN-DEFAULT CPAN-DEFAULT
 * perl-Mail-SPF CPAN-DEFAULT CPAN-DEFAULT
 * perl-MailTools CPAN-DEFAULT CPAN-DEFAULT
 * perl-Math-BigInt-FastCalc CPAN-DEFAULT CPAN-DEFAULT
 * perl-Math-Fibonacci-Phi CPAN-DEFAULT CPAN-DEFAULT
 * perl-Net-DNS CPAN-DEFAULT CPAN-DEFAULT
 * perl-Net-Ident CPAN-DEFAULT CPAN-DEFAULT
 * perl-Net-SPF CPAN-DEFAULT CPAN-DEFAULT
 * perl-Net-SSLeay CPAN-DEFAULT CPAN-DEFAULT
 * perl-Net-Server CPAN-DEFAULT CPAN-DEFAULT
 * perl-NetAddr-IP CPAN-DEFAULT CPAN-DEFAULT
 * perl-Parse-Syslog CPAN-DEFAULT CPAN-DEFAULT
 * perl-Perl-Critic CPAN-DEFAULT CPAN-DEFAULT
 * perl-Plack CPAN-DEFAULT CPAN-DEFAULT
 * perl-Pod-Escapes CPAN-DEFAULT CPAN-DEFAULT
 * perl-Pod-Simple CPAN-DEFAULT CPAN-DEFAULT
 * perl-SQL-Abstract CPAN-DEFAULT CPAN-DEFAULT
 * perl-SVN-Access CPAN-DEFAULT CPAN-DEFAULT
 * perl-Test-Deep CPAN-DEFAULT CPAN-DEFAULT
 * perl-Test-Exception CPAN-DEFAULT CPAN-DEFAULT
 * perl-Test-NoWarnings CPAN-DEFAULT CPAN-DEFAULT
 * perl-Test-Pod CPAN-DEFAULT CPAN-DEFAULT
 * perl-Test-Tester CPAN-DEFAULT CPAN-DEFAULT
 * perl-Tie-IxHash CPAN-DEFAULT CPAN-DEFAULT
 * perl-Time-HiRes CPAN-DEFAULT CPAN-DEFAULT
 * perl-Unix-PID CPAN-DEFAULT CPAN-DEFAULT
 * perl-Unix-Syslog CPAN-DEFAULT CPAN-DEFAULT
 * perl-VCS-Lite CPAN-DEFAULT CPAN-DEFAULT
 * perl-Variable-Magic CPAN-DEFAULT CPAN-DEFAULT
 * perl-WWW-Mechanize CPAN-DEFAULT CPAN-DEFAULT
 * perl-WWW-Mediawiki-Client CPAN-DEFAULT CPAN-DEFAULT
 * perl-WebService-Pushover CPAN-DEFAULT CPAN-DEFAULT
 * perl-rlib CPAN-DEFAULT CPAN-DEFAULT
 * perl-version CPAN-DEFAULT CPAN-DEFAULT
 * phpMyAdmin phpMyAdmin-([\d.]*?)-all-languages.tar.bz2 http://www.phpmyadmin.net/home_page/downloads.php
 * phpmyadmin phpMyAdmin-(2.*?)-all-languages.tar.bz2 http://www.phpmyadmin.net/home_page/downloads.php
 * pianobar DEFAULT http://6xq.net/static/projects/pianobar/
 * pnp4nagios DEFAULT SF-DEFAULT
 * postgrey DEFAULT http://postgrey.schweikert.ch/pub/
 * proftpd DEFAULT ftp://ftp.proftpd.org/distrib/source/
 * pure-ftpd DEFAULT http://download.pureftpd.org/pub/pure-ftpd/releases/
 * pydb DEFAULT http://bashdb.sourceforge.net/pydb/
 * python-webpy DEFAULT:web.py http://webpy.org/static/
 * razor-agents razor-agents-(.*?).tar.bz2 http://sourceforge.net/projects/razor/files/
 * re2c DEFAULT SF-DEFAULT
 * remake DEFAULT http://bashdb.sourceforge.net/remake/
 * remind DEFAULT http://www.roaringpenguin.com/files/download/
 * ripole DEFAULT http://www.pldaniels.com/ripole
 * rkhunter DEFAULT SF-DEFAULT
 * rrdtool DEFAULT http://oss.oetiker.ch/rrdtool/pub/
 * rsync DEFAULT http://rsync.samba.org/
 * rtorrent DEFAULT http://libtorrent.rakshasa.no/downloads/
 * siege DEFAULT http://www.joedog.org/pub/siege/
 * snappy DEFAULT GOOGLE-DEFAULT
 * spamassassin Mail-SpamAssassin-(.*?).tar.bz2 http://www.apache.org/dist/spamassassin/source/
 * spinner DEFAULT http://downloads.laffeycomputer.com/current_builds/spinner/
 * subversion DEFAULT http://subversion.apache.org/download/
 * swish-e DEFAULT http://swish-e.org/download/index.html
 * syslinux DEFAULT http://www.kernel.org/pub/linux/utils/boot/syslinux/
 * tig DEFAULT http://jonas.nitro.dk/tig/releases/
 * tinc tinc-([\d.]*?).tar.gz http://www.tinc-vpn.org/packages/
 * tmux DEFAULT SF-DEFAULT
 * tor DEFAULT http://tor.eff.org/dist/
 * ucarp DEFAULT http://download.pureftpd.org/pub/ucarp/
 * udpxy udpxy\.(.*?)-[\d]-prod.tgz SF-DEFAULT
 * unarj DEFAULT http://www.ibiblio.org/pub/Linux/utils/compress/
 * unbound DEFAULT http://unbound.net/downloads/
 * ungifsicle DEFAULT http://www.lcdf.org/gifsicle/
 * unhide DEFAULT SF-DEFAULT
 * unrar DEFAULT:unrarsrc http://www.rarlab.com/rar_add.htm
 * xmlrpc-c DEFAULT SF-DEFAULT
 * xournal DEFAULT SF-DEFAULT
 * zoo DEFAULT DEFAULT
 * pv DEFAULT http://www.ivarch.com/programs/pv.shtml
 * task DEFAULT http://taskwarrior.org/projects/show/taskwarrior
 * gocr DEFAULT http://jocr.sourceforge.net/download.html
 * gscan2pdf DEFAULT SF-DEFAULT
 * jailkit DEFAULT http://olivier.sessink.nl/jailkit/
 * perl-MIME-EncWords CPAN-DEFAULT CPAN-DEFAULT
 * perl-I18N-Charset CPAN-DEFAULT CPAN-DEFAULT
 * perl-MIME-Charset CPAN-DEFAULT CPAN-DEFAULT
 * perl-Email-Valid CPAN-DEFAULT CPAN-DEFAULT
 * perl-Mail-Sendmail CPAN-DEFAULT CPAN-DEFAULT
 * rsstail DEFAULT http://www.vanheusden.com/rsstail/
 * libmrss DEFAULT http://www2.autistici.org/bakunin/libmrss/
 * libnxml DEFAULT http://autistici.org/bakunin/codes.php
<!-- END LIST OF PACKAGES -->
            """

##testing list
#            page_text = """
#== List Of Packages ==
# * task DEFAULT http://taskwarrior.org/projects/show/taskwarrior
# * gifsicle DEFAULT http://www.lcdf.org/gifsicle/
# * perl-MailTools CPAN-DEFAULT CPAN-DEFAULT
# * unrar DEFAULT:unrarsrc http://www.rarlab.com/rar_add.htm
#<!-- END LIST OF PACKAGES -->
#            """
            #print page_text
            for package_data in sorted(helper.match_interval(page_text, package_line_regex, "== List Of Packages ==", "<!-- END LIST OF PACKAGES -->")):
#                print package_data
                (name, regex, url) = package_data
                nagging = True 
#                print "(name, regex, url)"
#                print name
#                print regex
#                print url
#                print repo
#                print scm
#                print br
#                print nagging
#               if name in ignore_packages:
#                   nagging = False
                packages.append(Package(name, regex, url, repo, scm, br, nagging=nagging))

        self.packages = packages
        #print "Packages"
        #print packages
        #print "Packages"
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
