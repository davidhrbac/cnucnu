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
import cmd
import readline

from cnucnu.package_list import Package, PackageList, Repository

class CheckShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        readline.set_completer_delims(' ')
        self.repo = Repository()
        self.package = Package("", None, None, self.repo)
        self._package_list = None
        self.prompt_default = " URL:"
        self.update_prompt()
        self.br = None

    @property
    def package_list(self):
        if not self._package_list:
            self._package_list = PackageList(repo=self.repo)
            self._package_list.append(self.package)
        return self._package_list

    def update_prompt(self):
        self.prompt = "%(name)s %(regex)s %(url)s " % self.package
        self.prompt += "%s> " % self.prompt_default

    def do_url(self, args):
        self.package.url = args

    def do_name(self, args):
        self.package.name = args
        if not self.package.regex:
            self.package.regex = "DEFAULT"
        if not self.package.url:
            self.package.url = "SF-DEFAULT"

    def do_fm(self, args):
        self.package.name = args
        self.package.regex = "FM-DEFAULT"
        self.package.url = "FM-DEFAULT"

    def do_inspect(self, args):
        try:
            self.package = self.package_list[args]
        except KeyError, ke:
            print ke

    def complete_inspect(self, text, line, begidx, endidx):
        package_names = [p.name for p in self.package_list if p.name.startswith(text)]
        return package_names
    
    def do_regex(self, args):
        self.package.regex = args

    def do_EOF(self, args):
        self.emptyline()


    def emptyline(self):
        if self.package.url:
            self.package.url = None
        else:
            print
            sys.exit(0)

    def default(self, args):
        if not self.package.url:
            self.do_url(args)
        else:
            self.do_regex(args)

    def postcmd(self, stop, line):
        if not self.package.url:
            self.prompt_default = " URL:"
        else:
            self.prompt_default = " Regex:"

        self.update_prompt()
        if self.package.url and self.package.regex:
            try:
                print "Versions:", self.package.upstream_versions
                print "Latest:", self.package.latest_upstream
                if self.package.name:
                    if self.package.status:
                        status = " %s" % self.package.status
                    else:
                        status = ""
                    print "Repo Version: %s%s" % (self.package.repo_version, status)
                    if self.package.upstream_newer:
                        open_bugs = self.br.get_open(self.package)
                        for bug in open_bugs:
                            print "Open Bug:", "https://bugzilla.redhat.com/show_bug.cgi?id=%s" % bug.bug_id
            except Exception, e:
                print e
        return stop

