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

from cnucnu.package_list import Package

class CheckShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        readline.set_completer_delims(' ')
        self.package = Package("", None, None, None)
        self.prompt_default = " URL:"
        self.update_prompt()

    def update_prompt(self):
        self.prompt = "%(url)s - %(regex)s" % self.package
        self.prompt += "%s> " % self.prompt_default

    def do_url(self, args):
        self.package.url = args

    def do_name(self, args):
        self.package.name = args
        if not self.package.regex:
            self.package.regex = "%s-([0-9.]*)\\.[tz][ai][rp]" % self.package.name
        if not self.package.url:
            self.package.url = "http://prdownloads.sourceforge.net/%s" % self.package.name
    
    def do_regex(self, args):
        self.package.regex = args

    def do_EOF(self, args):
        self.emptyline()

    def emptyline(self):
        if self.package.url:
            self.package.url = None
        else:
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
                print "Versions: ", self.package.upstream_versions
                print "Latest: ", self.package.latest_upstream
            except Exception, e:
                print e
        return stop

