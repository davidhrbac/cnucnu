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

from cnucnu.helper import cnucnu_cmp, cnucnu_max, split_rc

class HelperTest(unittest.TestCase):

    def test_cnucnu_cmp_basic(self):
        # equal
        self.assertEqual(cnucnu_cmp("0", "0"), 0)
        # first newer
        self.assertEqual(cnucnu_cmp("1", "0"), 1)
        # second newer
        self.assertEqual(cnucnu_cmp("0", "1"), -1)

    def test_split_rc(self):
        self.assertEqual(split_rc("4.0.0-rc1"), ("4.0.0", "1"))
        self.assertEqual(split_rc("4.0.0"), ("4.0.0", None))
        self.assertEqual(split_rc("0"), ("0", None))
        self.assertEqual(split_rc("1"), ("1", None))
        
        self.assertEqual(split_rc("4.0.0rc1"), ("4.0.0", "1"))

    def test_cnucnu_cmp_rc(self):
        self.assertEqual(cnucnu_cmp("4.0.0", "4.0.0"), 0)
        self.assertEqual(cnucnu_cmp("4.0.0", "4.0.0-rc1"), 1)
        self.assertEqual(cnucnu_cmp("4.0.0", "3.9.9-rc1"), 1)
        self.assertEqual(cnucnu_cmp("4.0.1-rc1", "4.0.0-rc1"), 1)
        self.assertEqual(cnucnu_cmp("4.0.1-rc1", "4.0.0"), 1)

        self.assertEqual(cnucnu_cmp("4.0.1rc1", "4.0.0"), 1)
        self.assertEqual(cnucnu_cmp("4.0.0", "4.0.0rc1"), 1)
        
        self.assertEqual(cnucnu_cmp("4.0.0-rc2", "4.0.0-rc1"), 1)
        self.assertEqual(cnucnu_cmp("4.0.0-rc2", "4.0.0rc1"), 1)
        self.assertEqual(cnucnu_cmp("4.0.0", "4.0.0-rc2"), 1)
        
        self.assertEqual(cnucnu_cmp("1.0.0", "1.0.0-rc1"), 1)

    def test_cnucnu_max(self):
        versions = ["4.0.1", "4.0.0", "4.0.0-rc2", "4.0.0rc1"]
        for i in range(0,len(versions) - 1):
            self.assertEqual(cnucnu_max(versions[i:]), versions[i])



    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(HelperTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main()
