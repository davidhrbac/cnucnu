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

DEFAULT_YAML="""
bugzilla:
    user: upstream-release-monitoring@fedoraproject.org
    password: 
    base url: https://bugzilla.redhat.com
    url: "%(base url)s/xmlrpc.cgi"
    bug url prefix: "%(base url)s/show_bug.cgi?id="
    product: Fedora
    version: rawhide
    keywords: FutureFeature
    bug status: ASSIGNED
    explanation url: 'https://fedoraproject.org/wiki/Using_FEver_to_track_upstream_changes'

    summary template: "%%(name)s-%%(latest_upstream)s is available"
    description template: 'Latest upstream release: %%(latest_upstream)s

                           Current version in %%(repo_name)s: %%(repo_version)s

                           URL: %%(url)s


                           More information about the service that created this bug can be found at:

    %(explanation url)s'


repo:
    path: 'http://download.fedora.redhat.com/pub/fedora/linux/development/source/SRPMS'
    name: Fedora Rawhide

cvs:
    viewvc_url: https://cvs.fedoraproject.org/viewvc/rpms/%(name)s/devel/sources?revision=HEAD
    cainfo: "fedora-server-ca.cert"

package list:
    mediawiki:
        base url: 'https://fedoraproject.org/w/'
        page: Using_FEver_to_track_upstream_changes


# vim: filetype=yaml
"""

class Config(object):
    def __init__(self, yaml_file=None, yaml=None, yaml_data=None, config=None, load_default=True):
        # TODO: remove yaml option
        if yaml_data:
            yaml = yaml_data
        self.config = {}

        # TODO?
        self.__getitem__ = self.config.__getitem__
        
        if load_default:
            self.update_yaml(DEFAULT_YAML)
        if yaml_file:
            self.update_yaml_file(yaml_file)
        elif yaml:
            self.update_yaml(yaml)
        elif config:
            self.update(config)

        self._bugzilla_config = {}

    def update_yaml_file(self, new_yaml_file, old=None):
        if not old:
            old = self.config
        file = open(new_yaml_file, "rb")
        new_yaml = file.read()
        file.close()

        old = self.update_yaml(new_yaml, old)
        return old

    def update_yaml(self, new_yaml, old=None):
        if not old:
            old = self.config
        new = yaml.load(new_yaml)
        old = self.update(new, old)
        return old

    def update(self, new, old=None):
        if not old:
            old = self.config
        for k, v in new.items():
            if k in old.keys():
                if isinstance(old[k], dict):
                    old[k] = self.update(new[k], old[k])
                else:
                    old[k] = new[k]
            else:
                old[k] = new[k]
        self._bugzilla_config = {}
        return old


#                D.update(E, **F) -> None.  Update D from E and F: for k in E: D[k] = E[k]
#                    (if E has keys else: for (k, v) in E: D[k] = v) then: for k in F: D[k] = F[k]


    @property
    def bugzilla_config(self):
        if not self._bugzilla_config:
            b = self.config["bugzilla"]
            for c, v in b.items():
                if isinstance(v, str):
                    b[c] = v % b

            self._bugzilla_config = b
        return self._bugzilla_config

    @property
    def bugzilla_class_conf(self):
        rpc_conf = filter_dict(self.bugzilla_config, ["url", "user", "password"])
        return rpc_conf

    @property
    def yaml(self):
        return yaml.dump(self.config, indent=4, default_flow_style=False)



if __name__ == '__main__':
    cf = Config()

    print "Default config"
    pprint(cf.config)

    cf.update_yaml_file('../../cnucnu.yaml')
    
    print "Global config"
    pprint(cf.config)

    print "\nBugzilla config"
    pprint(cf.bugzilla_config)

    print "\nBugzilla class config"
    pprint(cf.bugzilla_class_conf)

    print
    print cf.yaml
