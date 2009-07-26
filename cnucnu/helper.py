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
    return rpm.labelCompare((None, v1, None), (None, v2, None))

def rpm_max(list):
    list.sort(cmp=rpm_cmp)
    return list[-1]

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

