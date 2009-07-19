#!/usr/bin/python
# vim: fileencoding=utf8  foldmethod=marker
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

import unittest

import sys
sys.path.insert(0, '../..')

from cnucnu.package_list import Package
from cnucnu.package_list import Repository

class PackageTest(unittest.TestCase):

    def testCreatePackage(self):
        p = Package("name", "regex", "url", Repository())

    def testRegexUpdate(self):
        p = Package("name", "regex", "url", Repository())
        p._upstream_versions = [0, 1]
        p._latest_upstream = 1
        p._rpm_diff = 0 
        p.regex = "new regex"
        self.assertEqual(p.regex, "new regex")
        self.assertEqual(p._upstream_versions, None)
        self.assertEqual(p._latest_upstream, None)
        self.assertEqual(p._rpm_diff, None)
    
    def testUrlUpdate(self):
        p = Package("name", "regex", "url", Repository())
        p._upstream_versions = [0, 1]
        p._latest_upstream = 1
        p._rpm_diff = 1
        p.url = "new url"
        self.assertEqual(p.url, "new url")
        self.assertEqual(p._upstream_versions, None)
        self.assertEqual(p._latest_upstream, None)
        self.assertEqual(p._rpm_diff, None)
    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(PackageTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main()
