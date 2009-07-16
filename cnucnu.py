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

import sys
sys.path.insert(0, './lib')

import cnucnu.package_list as package_list
import cnucnu.checkshell as checkshell

if __name__ == '__main__':
    import re
    import cnucnu.errors as cc_errors

    from optparse import OptionParser
    parser = OptionParser()
     
    parser.add_option("", "--check", dest="check", help="check URL and regex interactively", action="store_true", default=False)

    (options, args) = parser.parse_args()

    if options.check:
        shell = checkshell.CheckShell()
        while True:
            try:
                if not shell.cmdloop():
                    break
            except Exception, ex: 
                print 'Exception occured:'
                print repr(ex)
                break
    else:
        repo = package_list.Repository(repoid="rawhide-source")
        plist = package_list.PackageList(repo=repo)
        packages = plist.packages

        package_nr = 0

        if package_nr == 0:
            mode = "w"
        else:
            mode = "a"


        outdated_f = open("cnucnu-outdated.log", mode)
        too_new_f = open("cnucnu-too_new.log", mode)
        error_f = open("cnucnu-error.log", mode)

        for package in packages[package_nr:]:
            sys.stderr.write("Testing: %i -  %s\n" % (package_nr, package.name))

            try:
                from cnucnu.helper import rpm_cmp
                diff = rpm_cmp(package.repo_version, package.latest_upstream) 
                if diff == -1:
                    print "Outdated package %(name)s: Rawhide version: %(repo_version)s, Upstream latest: %(latest_upstream)s" % package
                    outdated_f.write("%(name)s %(repo_version)s %(latest_upstream)s\n" % package)
                elif diff == 1:
                    print "Rawhide newer %(name)s: Rawhide version: %(repo_version)s, Upstream latest: %(latest_upstream)s" % package
                    too_new_f.write("%(name)s %(repo_version)s %(latest_upstream)s\n" % package)

            except cc_errors.UpstreamVersionRetrievalError, e:
                sys.stderr.write("%s\n" % str(e))
                sys.stderr.write("Rawhide Version: %s\n" % package.repo_version)
                error_f.write("%s: %s - Rawhide Version: %s\n" % (package.name, str(e), package.repo_version))
            except KeyError, ke:
                sys.stderr.write("Package not found in Rawhide: %s\n" % str(ke))

            package_nr = package_nr + 1

        outdated_f.close()
        too_new_f.close()
        error_f.close()
