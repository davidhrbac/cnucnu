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

from bugzilla import Bugzilla
from config import Config
from helper import filter_dict
from helper import pprint

class BugzillaReporter(object):
    base_query = {'query_format': ['advanced'], 'emailreporter1': ['1'], 'emailtype1': ['exact']}

    bug_status_open = ['NEW', 'ASSIGNED', 'MODIFIED', 'ON_DEV', 'ON_QA', 'VERIFIED', 'FAILS_QA', 'RELEASE_PENDING', 'POST']
    bug_status_closed = ['CLOSED']

    new_bug = { 'status': 'NEW',
# Using ASSIGNED returns an exception:
# <Fault 32000: 'You are not allowed to file new bugs with the\n      ASSIGNED status.'>
# if the account is in editbugs, fedora_bugs, fedora_contrib, setpriority
# if not, then it is silently ignored
#               'status': 'ASSIGNED',
            }
            
    def __init__(self, config):
        rpc_conf = filter_dict(config, ["url", "user", "password"])
        bz = Bugzilla(**rpc_conf)
        self.bz = bz

        if "password" in rpc_conf and rpc_conf["password"]:
            self.bz.login()
        self.bugzilla_config = config

        self.base_query['product'] = config['product']
        self.base_query['email1'] = config['user']
        self.new_bug['product'] = config['product']
        if "keywords" in config:
            self.new_bug['keywords'] = config['keywords']
        self.new_bug['version'] = config['version']

        self.bugzilla_username = config['user']


    def bug_url(self, bug):
        if isinstance(bug, str):
            bug_id = bug
        else:
            bug_id = bug.bug_id

        return "%s%s" % (self.bugzilla_config['bug url prefix'], bug_id)

    def report_outdated(self, package, dry_run=True):
        if package.upstream_newer:
            matching_bugs = self.get_bug(package)
            # TODO: warning in case of more than one matching bug, then something is wrong
            if not matching_bugs:
                open = self.get_open(package)
                if not open:
                    bug = {'component': package.name,
                           'summary': self.config["summary template"] % package,
                           'description': self.config["description template"] % package
                            }
                    bug.update(self.new_bug)

                    if not dry_run:
                        new_bug = self.bz.createbug(**bug)
                        status = self.config['status']
                        if status != "NEW":
                            change_status = self.bz._proxy.bugzilla.changeStatus(new_bug.bug_id, status, self.config['user'], "", "", False, False, 1)
                            print "status changed", change_status
                        print self.bug_url(new_bug)
                    else:
                        pprint(bug)
                else:
                    open_bug = open[0]
                    summary = open_bug.summary

                    # summary should be '<name>-<version> <some text>'
                    # To extract the version get everything before the first space
                    # with split and then remove the name and '-' via slicing
                    bug_version = summary.split(" ")[0][len(package.name)+1:]

                    if bug_version != package.latest_upstream:
                        # :TODO: comment creation untested
                        update = {'short_desc': self.config["summary template"] % package,
                                  'comment': self.config["summary template"] % package
                                 }
                        res = self.bz._update_bugs(open_bug.bug_id, update)
                        print res
                        return res
            else:
                for bug in matching_bugs:
                    print "bug already filed:%s %s" % (self.bug_url(bug), bug.bug_status)

    def get_bug(self, package):
        q = {'component': [package.name],
             'bug_status': self.bug_status_open + self.bug_status_closed,
             'short_desc': ['%(name)s-%(latest_upstream)s' % package],
             'short_desc_type': ['substring']
            }
       
        q.update(self.base_query)
        bugs = self.bz.query(q)
        return bugs

    def get_open(self, package):
        q = {'component': [package.name],
             'bug_status': self.bug_status_open
            }

        q.update(self.base_query)
        return self.bz.query(q)
