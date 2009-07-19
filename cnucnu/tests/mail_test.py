#!/usr/bin/python
# vim: fileencoding=utf8  foldmethod=marker
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

import unittest

import sys
sys.path.insert(0, '../..')


from cnucnu.mail import Message

class MailTest(unittest.TestCase):

    def testCreateMessage(self):
        m = Message("me@example.com", "you@example.com", "subject", "message")

    def testMessageEncoding(self):
        sender = "Mr. Umläut <u@example.com>"
        receipient = "ß <l@example.com>"
        subject = "ä"
        message = "Ö"
        
        m = Message(sender, receipient, subject, message)
        self.assertEqual(m.receipient, receipient)
        self.assertEqual(m.sender, sender)
        message_string = 'MIME-Version: 1.0\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: base64\nSubject: =?utf-8?b?w6Q=?=\nFrom: =?utf-8?b?TXIuIFVtbMOkdXQ=?= <u@example.com>\nTo: =?utf-8?b?w58=?= <l@example.com>\n\nw5Y=\n'
        self.assertEqual(message_string, m.as_string())
    
    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(MailTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main()
