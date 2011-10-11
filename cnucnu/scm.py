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

# Options: http://curl.haxx.se/libcurl/c/curl_easy_setopt.html

from helper import secure_download
from config import global_config

class SCM(object):
    """ cainfo: filename :-/
    """
    def __init__(self, view_scm_url="", cainfo=""):
        defaults = global_config.config["scm"]

        if not view_scm_url:
            view_scm_url = defaults["view_scm_url"]

        if not cainfo:
            cainfo = defaults["cainfo"]

        self.view_scm_url = view_scm_url
        self.cainfo = cainfo

    def get_sources(self, package):
        return secure_download(self.view_scm_url % package, cainfo=self.cainfo)

    def get_sourcefiles(self, package):
        sources = self.get_sources(package)
        sourcefiles = []
        for line in sources.split("\n"):
            if line != "":
                file = line.split(" ")[2]
                sourcefiles.append(file)

        return sourcefiles

    def has_upstream_version(self, package):
        sourcefiles = self.get_sourcefiles(package)
        for file in sourcefiles:
            if package.latest_upstream in file:
                return True
        return False



if __name__ == '__main__':
    scm = SCM(**{"view_scm_url": "https://pkgs.fedoraproject.org/gitweb/?p=%(name)s.git;a=blob_plain;f=sources;hb=refs/heads/master", "cainfo": "fedora-server-ca.cert"})

    from package_list import Package, Repository


    import sys
    package_name = len(sys.argv) > 1 and sys.argv[1] or "crossvc"

    package = Package(package_name, "", "", Repository())
    upstream_version = len(sys.argv) > 2 and sys.argv[1] or "1.5.2-0"
    package._latest_upstream = upstream_version

    print scm.get_sources({"name": package_name})
    print scm.get_sourcefiles({"name": package_name})
    print scm.has_upstream_version(package)

