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

from cnucnu.helper import upstream_cmp, upstream_max, split_rc, cmp_upstream_repo, get_rc

class HelperTest(unittest.TestCase):

    def test_upstream_cmp_basic(self):
        # equal
        self.assertEqual(upstream_cmp("0", "0"), 0)
        # first newer
        self.assertEqual(upstream_cmp("1", "0"), 1)
        # second newer
        self.assertEqual(upstream_cmp("0", "1"), -1)

    def test_split_rc(self):
        self.assertEqual(split_rc("4.0.0-rc1"), ("4.0.0", "rc1"))
        self.assertEqual(split_rc("4.0.0-pre2"), ("4.0.0", "pre2"))
        self.assertEqual(split_rc("4.0.0"), ("4.0.0", ""))
        self.assertEqual(split_rc("0"), ("0", ""))
        self.assertEqual(split_rc("1"), ("1", ""))
        
        self.assertEqual(split_rc("4.0.0rc1"), ("4.0.0", "rc1"))

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
        
        self.assertEqual(upstream_cmp("1.0.0", "1.0.0-rc1"), 1)
    
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

    def test_upstream_max_rc(self):
        versions = ["4.0.1", "4.0.0", "4.0.0-rc2", "4.0.0rc1"]
        for i in range(0,len(versions) - 1):
            self.assertEqual(upstream_max(versions[i:]), versions[i])
    
    def test_upstream_max_pre(self):
        versions = ["4.0.1", "4.0.0", "4.0.0-pre2", "4.0.0pre1"]
        for i in range(0,len(versions) - 1):
            self.assertEqual(upstream_max(versions[i:]), versions[i])


    def test_get_rc(self):
        self.assertEqual(get_rc("0.4.pre2.fc11"), "pre2")

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


    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(HelperTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main()
