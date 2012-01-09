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

import smtplib, email
from email import MIMEText
from email import Header
#from email import _parseaddr, _formataddr


def encode_addr(addr):
    real_name, email_address = parseaddr(addr)
    try:
        # check for non-ascii characters
        real_name = real_name.encode("ascii")
    except (UnicodeEncodeError, UnicodeDecodeError), e:
        real_name = str(Header(ensure_encoding(real_name), "UTF-8"))
    return formataddr((real_name, email_address))

def ensure_encoding(text, encoding="UTF-8"):
        try:
            text = text.encode("UTF-8")
        #  text not a unicode string like e.g. u"unicode string"
        # Assume that it is encoded in UTF-8 for convenience
        except UnicodeDecodeError, e:
            text = text.decode("UTF-8").encode("UTF-8")

        return text

class Message:
    def __init__(self, sender, receipient, subject, message):
        self.sender = sender
        self.receipient = receipient

        msg = MIMEText(ensure_encoding(message), _charset="UTF-8")
        msg['Subject'] = Header(ensure_encoding(subject), "UTF-8")
        msg['From'] = encode_addr(sender)
        msg['To'] = encode_addr(receipient)

        self.msg = msg
        self.as_string = msg.as_string


class Mailer:
    def __init__(self, smtp_host):
        self.smtp_host = smtp_host

    def send(self, message):

        s = smtplib.SMTP(self.smtp_host)
        s.sendmail(message.sender, [message.receipient], message.as_string())
        s.quit()

message_template_outdated = """ The latest upstream release for %(name)s is %(latest_upstream)s, but Fedora Rawhide only contains %(repo_version)s.

This mail is sent, because your package is listed at:
https://fedoraproject.org/wiki/Using_FEver_to_track_upstream_changes

Eventually, there will be bugs filed for outdated packages, but this is not yet implemented.
"""


if __name__ == "__main__":
    mailer = Mailer(smtp_host="")

    data_file = open("../../data.pickle")
