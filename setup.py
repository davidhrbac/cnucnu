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

from distutils.core import setup
setup(name='cnucnu',
      description='Upstream monitoring for Fedora',
      version='0.0.0',
      license='GPLv2+',
      author='Till Maas',
      author_email='opensource@till.name',
      url='http://fedorapeople.org/gitweb?p=till/public_git/cnucnu.git;a=summary',
      scripts=['bin/cnucnu'],
      package_dir = {'': 'lib'},
      packages = ['cnucnu'],
     )

