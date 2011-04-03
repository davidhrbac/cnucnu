#!/usr/bin/python
# vim: fileencoding=utf8  foldmethod=marker
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

import unittest

import sys
sys.path.insert(0, '../..')

from cnucnu.helper import upstream_cmp, upstream_max, split_rc, cmp_upstream_repo, get_rc, get_html, expand_subdirs

class HelperTest(unittest.TestCase):

    def test_upstream_cmp_basic(self):
        # equal
        self.assertEqual(upstream_cmp("0", "0"), 0)
        # first newer
        self.assertEqual(upstream_cmp("1", "0"), 1)
        # second newer
        self.assertEqual(upstream_cmp("0", "1"), -1)

    def test_split_rc(self):
        self.assertEqual(split_rc("4.0.0-rc1"), ("4.0.0", "rc", "1"))
        self.assertEqual(split_rc("4.0.0-pre2"), ("4.0.0", "pre", "2"))
        self.assertEqual(split_rc("4.0.0"), ("4.0.0", "", ""))
        self.assertEqual(split_rc("0"), ("0", "", ""))
        self.assertEqual(split_rc("1"), ("1", "", ""))
        self.assertEqual(split_rc("1.2pre"), ("1.2", "pre", ""))
        self.assertEqual(split_rc("4.0.0RC1"), ("4.0.0", "RC", "1"))
        self.assertEqual(split_rc("4.0.0-PRE2"), ("4.0.0", "PRE", "2"))
        self.assertEqual(split_rc("4.0.0rc1"), ("4.0.0", "rc", "1"))

    def test_upstream_cmp_rc(self):
        self.assertEqual(upstream_cmp("4.0.0", "4.0.0"), 0)
        self.assertEqual(upstream_cmp("4.0.0", "4.0.0-rc1"), 1)
        self.assertEqual(upstream_cmp("4.0.0", "4.0.0-RC1"), 1)
        self.assertEqual(upstream_cmp("4.0.0", "3.9.9-rc1"), 1)
        self.assertEqual(upstream_cmp("4.0.1-rc1", "4.0.0-rc1"), 1)
        self.assertEqual(upstream_cmp("4.0.1-rc1", "4.0.0"), 1)
        self.assertEqual(upstream_cmp("4.0.1-RC1", "4.0.0"), 1)

        self.assertEqual(upstream_cmp("4.0.1rc1", "4.0.0"), 1)
        self.assertEqual(upstream_cmp("4.0.1RC1", "4.0.0"), 1)
        self.assertEqual(upstream_cmp("4.0.0", "4.0.0rc1"), 1)

        self.assertEqual(upstream_cmp("4.0.0-rc2", "4.0.0-rc1"), 1)
        self.assertEqual(upstream_cmp("4.0.0-rc2", "4.0.0rc1"), 1)
        self.assertEqual(upstream_cmp("4.0.0", "4.0.0-rc2"), 1)
        self.assertEqual(upstream_cmp("1.0.0rc3", "1.0.0RC3"), 0)
        self.assertEqual(upstream_cmp("1.0.0", "1.0.0-rc1"), 1)
        self.assertEqual(upstream_cmp("1.0.0rc3", "1.0.0-RC21"), -1)
        self.assertEqual(upstream_cmp("1.0.0rc10", "1.0.0-rc0010"), 0)

    def test_upstream_cmp_pre(self):
        self.assertEqual(upstream_cmp("4.0.0", "4.0.0"), 0)
        self.assertEqual(upstream_cmp("4.0.0", "4.0.0-pre1"), 1)
        self.assertEqual(upstream_cmp("4.0.0", "3.9.9-pre1"), 1)
        self.assertEqual(upstream_cmp("4.0.1-pre1", "4.0.0-pre1"), 1)
        self.assertEqual(upstream_cmp("4.0.1-pre1", "4.0.0"), 1)

        self.assertEqual(upstream_cmp("4.0.1pre1", "4.0.0"), 1)
        self.assertEqual(upstream_cmp("4.0.0", "4.0.0pre1"), 1)

        self.assertEqual(upstream_cmp("4.0.0-pre2", "4.0.0-pre1"), 1)
        self.assertEqual(upstream_cmp("4.0.0-pre2", "4.0.0pre1"), 1)
        self.assertEqual(upstream_cmp("4.0.0", "4.0.0-pre2"), 1)

        self.assertEqual(upstream_cmp("1.0.0", "1.0.0-pre1"), 1)
        self.assertEqual(upstream_cmp("1.0.0PRE1", "1.0.0pre1"), 0)
        self.assertEqual(upstream_cmp("1.0.0pre15", "1.0.0pre2"), 1)
        self.assertEqual(upstream_cmp("1.0pre5", "1.0pre05"), 0)

    def test_upstream_max_rc(self):
        versions = ["4.0.1", "4.0.0", "4.0.0-rc2", "4.0.0rc1"]
        for i in range(0,len(versions) - 1):
            self.assertEqual(upstream_max(versions[i:]), versions[i])

    def test_upstream_max_sorted(self, versions=["2", "1"]):
        """ versions is expected to be sorted, newest version first """
        for i in range(0,len(versions) - 1):
            self.assertEqual(upstream_max(versions[i:]), versions[i])

    def test_upstream_max(self, versions=["1", "2"], expected="2"):
        self.assertEqual(upstream_max(versions), expected)

    def test_upstream_max_pre(self):
        self.test_upstream_max_sorted(["4.0.1", "4.0.0", "4.0.0-pre2", "4.0.0pre1"])
        self.test_upstream_max_sorted(["1.2.1", "1.2b", "1.2a", "1.2", "1.2pre"])
        self.test_upstream_max_sorted(["1.3", "1.2"])

    def test_upstream_max_allrc(self):
        self.test_upstream_max_sorted(["1.0.1pre0", "1.0", "1.0-rc11", "1.0RC3", "1.0RC", "1.0-PRE10", "1.0pre1", "1.0pre0", "1.0pre"])

#    def test_perl_versioning(self):
#        """ 1.20 is newer than 1.902 """
#        self.test_upstream_max_sorted(["1.20", "1.902", "1.901", "1.18"])

#    def test_upstream_gnu_prerelease(self):
#        """ 1.2a and 1.2b are preleases here """
#        self.test_upstream_max_sorted(["1.2", "1.2a", "1.2b", "1.1"])

    def test_get_rc(self):
        self.assertEqual(get_rc("0.4.pre2.fc11"), ("pre", "2"))
        self.assertEqual(get_rc("0.4.RC1.fc15"), ("RC", "1"))
        self.assertEqual(get_rc("0.11.rc15.el5"), ("rc", "15"))

    def test_cmp_upstream_repo(self):
        self.assertEqual(cmp_upstream_repo("0.1.0", ("0.1.0", "5.fc10")), 0)
        self.assertEqual(cmp_upstream_repo("0.1.0", ("0.1.0", "")), 0)
        self.assertEqual(cmp_upstream_repo("0.1.1", ("0.1.0", "5.fc10")), 1)
        self.assertEqual(cmp_upstream_repo("0.1.0", ("0.2.0", "5.fc10")), -1)

    def test_cmp_upstream_repo_pre(self):
        upstream_v = "0.6.0pre2"
        repo_vr = ("0.6.0", "0.4.pre2.fc11")
        repo_vr_older = ("0.5.9", "0.4.pre2.fc11")
        repo_vr_newer = ("0.6.0", "1.fc11")
        self.assertEqual(cmp_upstream_repo(upstream_v, repo_vr), 0)
        self.assertEqual(cmp_upstream_repo(upstream_v, repo_vr_older), 1)
        self.assertEqual(cmp_upstream_repo(upstream_v, repo_vr_newer), -1)

    def test_get_html(self):
        import StringIO
        from cnucnu.helper import reactor

        http_url = ("http://www.fedoraproject.org")
        res = StringIO.StringIO()

        http_url = expand_subdirs(http_url)
        data1 = get_html(http_url)

        callback = [res.write, lambda ignore: reactor.stop()]
        get_html(http_url, callback=callback)
        reactor.run()
        data2 = res.getvalue()
        res.close()

        self.assertEqual(data1, data2)

    def test_snapshot_version_with_dash(self):
       # first newer
        self.assertEqual(upstream_cmp("1.8.23-20100128-r1100", "1.8.23-20091230-r1079"), 1)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(HelperTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main()
