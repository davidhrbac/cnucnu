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

from helper import pprint, filter_dict
import yaml

class Config(object):
    def __init__(self, yaml_filename):
        file = open(yaml_filename, "rb")
        self.config = yaml.load(file.read())
        file.close()

        self._bugzilla_config = {}

    @property
    def bugzilla_config(self):
        if not self._bugzilla_config:
            b = self.config["bugzilla"]
            for c, v in b.items():
                b[c] = v % b

            self._bugzilla_config = b
        return self._bugzilla_config

    @property
    def bugzilla_class_conf(self):
        rpc_conf = filter_dict(self.bugzilla_config, ["url", "user", "password"])
        return rpc_conf


if __name__ == '__main__':
    cf = Config('../../cnucnu.yaml')
    print "Global config"
    pprint(cf.config)

    print "\nBugzilla config"
    pprint(cf.bugzilla_config)

    print "\nBugzilla class config"
    pprint(cf.bugzilla_class_conf)
