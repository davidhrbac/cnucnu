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
""" :author: Till Maas
    :contact: till.maas@till.name
    :license: GPLv2+
"""
__docformat__ = "restructuredtext"

#from genshi.template import MarkupTemplate
from genshi.template import TemplateLoader
from package_list import PackageList

if __name__ == "__main__":
    loader = TemplateLoader(["templates"])
    tmpl = loader.load('status.html')
    packages = PackageList()
    stream = tmpl.generate(packages=packages)
    print stream.render()

