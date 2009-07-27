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

import pprint as pprint_module
pp = pprint_module.PrettyPrinter(indent=4)
pprint = pp.pprint

def get_html(url):
    if url.startswith("ftp://"):
        import urllib
        req = urllib.urlopen(url)
        return req.read()
    else:
        import pycurl
        import StringIO

        c = pycurl.Curl()
        c.setopt(pycurl.URL, url.encode("ascii"))

        res = StringIO.StringIO()

        c.setopt(pycurl.WRITEFUNCTION, res.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 10)

        c.perform()
        c.close()
        data = res.getvalue()
        res.close()

        return data

def rpm_cmp(v1, v2):
    import rpm
    diff = rpm.labelCompare((None, v1, None), (None, v2, None))
    return diff

def rpm_max(list):
    list.sort(cmp=rpm_cmp)
    return list[-1]

def upstream_cmp(v1, v2):
    import rpm

    v1, rc1 = split_rc(v1)
    v2, rc2 = split_rc(v2)

    diff = rpm_cmp(v1, v2)
    # base versions are the same, check for rc-status
    if diff == 0:
        # both are rc, higher rc is newer
        if rc1 and rc2:
            return cmp(rc1, rc2)
        # only first is rc, then second is newer
        elif rc1:
            return -1
        # only second is rc, then first is newer
        elif rc2:
            return 1
        # none is rc, both are the same
        else:
            return 0
    # base versions are different, ignore rc-status
    else:
        return diff

def split_rc(version):
    import re
    RC = re.compile("([^-rp]*)(-?(([Rr][Cc]|[Pp][Rr][Ee])[0-9]))?")
    match = RC.match(version)

    v = match.groups()[0]
    rc = match.groups()[2]
    if rc:
        return (v, rc)
    else:
        return (v, "")

def get_rc(release):
    import re
    RC = re.compile(r'0\.[0-9]*\.(([Rr][Cc]|[Pp][Rr][Ee])[0-9])')
    match = RC.match(release)

    if match:
        rc = match.groups()[0]
        return rc
    else:
        return ""

def upstream_max(list):
    list.sort(cmp=upstream_cmp)
    return list[-1]

def cmp_upstream_repo(upstream_v, repo_vr):
    repo_rc = get_rc(repo_vr[1])

    repo_version = "%s%s" % (repo_vr[0], repo_rc)

    return upstream_cmp(upstream_v, repo_version)



""" return a dict that only contains keys that are in key_list
"""
def filter_dict(d, key_list):
    return dict([v for v in d.items() if v[0] in key_list])

def secure_download(url, cainfo=""):
    import pycurl
    import StringIO

    c = pycurl.Curl()
    c.setopt(pycurl.URL, url.encode("ascii"))

    # -k / --insecure
    # c.setopt(pycurl.SSL_VERIFYPEER, 0)

    # Verify certificate
    c.setopt(pycurl.SSL_VERIFYPEER, 1)

    # Verify CommonName or Subject Alternate Name
    c.setopt(pycurl.SSL_VERIFYHOST, 2)

    # --cacert
    if cainfo:
        c.setopt(pycurl.CAINFO, cainfo)

    res = StringIO.StringIO()

    c.setopt(pycurl.WRITEFUNCTION, res.write)

    # follow up to 10 http location: headers
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 10)

    c.perform()
    c.close()
    data = res.getvalue()
    res.close()

    return data

