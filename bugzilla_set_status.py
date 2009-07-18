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

# Set status of bugs to ASSGINED and add FutureFeature keyword to follow triage workflow
# The upstream-release-monitoring account cannot do this currently, therefor this needs
# to be done by a more privileged account

# Bugzilla webservice docs:
# https://bugzilla.redhat.com/docs/en/html/api/extensions/compat_xmlrpc/code/webservice.html

from bugzilla import Bugzilla
import getpass

import pprint as pprint_module
pp = pprint_module.PrettyPrinter(indent=4)
pprint = pp.pprint

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-u", "--username", dest="username", help="bugzilla username")

(options, args) = parser.parse_args()




bz = Bugzilla(url="https://bugzilla.redhat.com/xmlrpc.cgi")

qs = {'product': ['Fedora'], 'query_format': ['advanced'], 'bug_status': ['NEW'], 'emailreporter1': ['1'], 'emailtype1': ['exact'], 'email1': ['upstream-release-monitoring@fedoraproject.org']}

bugs = bz.query(qs)

pprint(bugs)

username = options.username
if not username:
    username = raw_input("Username: ")

bz.login(user=username, password=getpass.getpass())
# :TODO:
# Maybe all bugs could be changed somehow like this:
#
#update = {'bug_status': 'ASSIGNED',
#          'keywords': 'FutureFeature'
#         }
#bug_id_list = [b.bug_id for b in bugs]
#bz._update_bugs(bug_id_list, update)


def set_FutureFeature(bug_id):
    kw_defaults = {'nomail': 1, 'action': 'add', 'keywords': 'FutureFeature'}
    kw = {"bug_id": bug_id}
    kw.update(kw_defaults)
    return bz._proxy.bugzilla.updateKeywords(kw, username, "")

def set_ASSIGNED(bug_id):
    return bz._proxy.bugzilla.changeStatus(bug_id, "ASSIGNED", username, "", "", False, False, 1)

if __name__ == '__main__':
    for bug in bugs:
        print "changing: %s" % bug.bug_id
        print "https://bugzilla.redhat.com/show_bug.cgi?id=%s" % bug.bug_id

        # :TODO: setstatus seems still to send mails, therefore the raw interface is used
        #bug.setstatus("ASSIGNED", nomail=1)
        set_ASSIGNED(bug.bug_id)
        set_FutureFeature(bug.bug_id)
