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
import os

from cnucnu.config import global_config
from cnucnu.package_list import Repository, PackageList, Package
from cnucnu.checkshell import CheckShell
from cnucnu.bugzilla_reporter import BugzillaReporter
from cnucnu.scm import SCM

import pprint as pprint_module
pp = pprint_module.PrettyPrinter(indent=4)
pprint = pp.pprint

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option("", "--shell", dest="action", help="Interactive shell", action="store_const", const="shell")
    parser.add_option("", "--config", dest="config_filename", help="config_filename, e.g. for bugzilla credentials")
    parser.add_option("", "--create-bugs", dest="action", help="file bugs for outdated packages", action="store_const", const="create-bugs")
    parser.add_option("", "--fm-outdated-all", dest="action", help="compare all packages in rawhide with freshmeat", action="store_const", const="fm-outdated-all")
    parser.add_option("", "--dump-config", dest="action", help="dumps dconfig to stdout", action="store_const", const="dump-config")
    parser.add_option("", "--dump-default-config", dest="action", help="dumps default config to stdout", action="store_const", const="dump-default-config")
    parser.add_option("", "--dry-run", dest="dry_run", help="Do not file or change bugs", default=False)
    parser.add_option("", "--start-with", dest="start_with", help="Start with this package when reporting bugs", metavar="PACKAGE", default="")

    (options, args) = parser.parse_args()

    if options.action == "dump-default-config":
        sys.stdout.write(global_config.yaml)
        sys.exit(0)


    # default to ./cnucnu.yaml if it exists and no config file is specified on
    # the commandline
    yaml_file = options.config_filename
    if not yaml_file:
        new_yaml_file = "./cnucnu.yaml"
        if os.access(new_yaml_file, os.R_OK):
            yaml_file = new_yaml_file

    if yaml_file:
        global_config.update_yaml_file(yaml_file)

    if options.action == "dump-config":
        sys.stdout.write(global_config.yaml)
        sys.exit(0)

    if options.action == "shell":
        shell = CheckShell(config=global_config)
        while True:
            if not shell.cmdloop():
                break

    elif options.action == "create-bugs":
        br = BugzillaReporter(global_config.bugzilla_config)
        repo = Repository(**global_config.config["repo"])
        scm = SCM(**global_config.config["scm"])

        outdated = []

        pl = PackageList(repo=repo, scm=scm, br=br, **global_config.config["package list"])
        for p in pl:
            if p.name >= options.start_with:
                print "testing: %s" % p.name
                try:
                    if p.upstream_newer:
                       pprint(p.report_outdated(dry_run=options.dry_run))
                except Exception, e:
                    pprint(e)
            else:
                print "skipping: %s" % p.name


    elif options.action == "fm-outdated-all":
        print "checking all against FM"
        repo = Repository()
        package_names = [name for name in repo.repoquery()]
        pl=[Package(name, "FM-DEFAULT", "FM-DEFAULT", repo) for name in package_names]
        packages = PackageList(packages=pl)
        repo.package_list = packages
        analyse_packages(packages)
