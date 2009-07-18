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
import pprint as pprint_module
pp = pprint_module.PrettyPrinter(indent=4)
pprint = pp.pprint

class BugzillaReporter(object):
    base_query = {'query_format': ['advanced'], 'emailreporter1': ['1'], 'emailtype1': ['exact']}

    bug_status_open = ['NEW', 'ASSIGNED', 'MODIFIED', 'ON_DEV', 'ON_QA', 'VERIFIED', 'FAILS_QA', 'RELEASE_PENDING', 'POST']
    bug_status_closed = ['CLOSED']

    new_bug = {'version': 'rawhide',
               'status': 'ASSIGNED',
               'keywords': 'FutureFeature'
            }

    description_template = \
"""Latest upstream release: %(latest_upstream)s
Current version in %(repo_name)s: %(repo_version)s
URL: %(url)s

More information about the service that created this bug can be found at:
https://fedoraproject.org/wiki/Using_FEver_to_track_upstream_changes"""
            
    def __init__(self, bugzilla_url, bugzilla_username, bugzilla_password, bugzilla_product):
        bz = Bugzilla(url=bugzilla_url, user=bugzilla_username, password=bugzilla_password)
        self.bz = bz
        self.bz.login()
        self.product = bugzilla_product
        self.base_query['product'] = [bugzilla_product]
        self.base_query['email1'] = [bugzilla_username]
        self.new_bug['product'] = bugzilla_product


    def report_outdated(self, package, dry_run=True):
        if package.upstream_newer:
            matching_bugs = self.get_bug(package)
            # TODO: warning in case of more than one matching bug, then something is wrong
            if not matching_bugs:
                open = self.get_open(package)
                if not open:
                    bug = {'component': package.name,
                           'summary': "%(name)s-%(latest_upstream)s is available" % package,
                           'description': self.description_template % package
                            }
                    bug.update(self.new_bug)

                    if not dry_run:
                        new_bug = self.bz.createbug(**bug)
                        print "https://bugzilla.redhat.com/show_bug.cgi?id=%s" % new_bug.bug_id
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
                        # :TODO:
                        print "bug needs to be updated, but python-bugzilla seems not to support updating summary"
            else:
                for bug in matching_bugs:
                    print "bug already filed: https://bugzilla.redhat.com/show_bug.cgi?id=%s %s" % (bug.bug_id, bug.bug_status)

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
