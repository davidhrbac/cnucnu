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

from cnucnu.config import Config

class ConfigTest(unittest.TestCase):

    def testCreateConfig(self):
        c = Config()
        c = Config(yaml="{}")
        c = Config(config={})

    def testSimpleUpdate(self):
        old = {0: 0, "d": {0: 0}}
        new = {1: 1, "d": {1: 1}}
        expected = {0: 0, 1: 1, "d": {0: 0, 1: 1}}

        c = Config(config=old, load_default=False)
        c.update(new)

        self.assertEqual(c.config, expected)
    
    def testComplexUpdate(self):
        old = {0: 0, "d": {0: 0, 1: 1, 2: 2}, 2: {}}
        new = {1: 1, "d": {1: {0: 0}, 2: None}}
        expected = {0: 0, 1: 1, "d": {0: 0, 1: {0: 0}, 2: None}, 2: {}}

        c = Config(config=old, load_default=False)
        c.update(new)

        self.assertEqual(c.config, expected)
    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ConfigTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main()
