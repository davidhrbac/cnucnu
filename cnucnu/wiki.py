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

import fedora.client

class MediaWiki(fedora.client.Wiki):
    def __init__(self, base_url='https://fedoraproject.org/w/', *args, **kw):
        super(MediaWiki, self).__init__(base_url, *args, **kw)

    def json_request(self, method="api.php", req_params=None, auth=False, **kwargs):
        if req_params:
            req_params["format"] = "json"

        data =  self.send_request(method, req_params, auth, **kwargs)

        if 'error' in data:
            raise Exception(data['error']['info'])
        return data

    def get_pagesource(self, titles):
        data = self.json_request(req_params={
                'action' : 'query',
                'titles' : titles,
                'prop'   : 'revisions',
                'rvprop' : 'content'
                }
                )
        return data['query']['pages'].popitem()[1]['revisions'][0]['*']


if __name__ == '__main__':
    wiki = MediaWiki(base_url='https://fedoraproject.org/w/')
    print wiki.get_pagesource("Upstream_release_monitoring")
