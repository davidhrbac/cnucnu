#!/usr/bin/python
# vim: fileencoding=utf8 foldmethod=marker
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

import ConfigParser

class Config(object):
    def __init__(self, ini_filename):
        ini = ConfigParser.ConfigParser()
        self.ini = ini

        file = open(ini_filename, "rb")
        ini.readfp(file)
        file.close()

        self._bugzilla_config = {}

    @property
    def bugzilla_config(self):
        if not self._bugzilla_config:
            for name, value in self.ini.items("cnucnu"):
                bugzilla_prefix = "bugzilla "
                if name.startswith(bugzilla_prefix):
                    self._bugzilla_config["bugzilla_"+name[len(bugzilla_prefix):]] = value
        return self._bugzilla_config
