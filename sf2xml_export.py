#!/usr/bin/env python
#
# (C) Copyright IBM Corp. 2006
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. This
# file and program are licensed under a BSD style license. See
# the Copying file included with the OpenHPI distribution for
# full licensing terms.
#
"""
Fetch the SourceForge XML export file for the project.
Need to have admin privileges on SF to use this.

Author(s):
        Renier Morales <renierm@users.sf.net>
        Shyamala Hirepatt <shyamala.hirepatt@hp.com>
        Mohan Devarajulu <mohan@fc.hp.com>
"""
import sys, os, time
from optparse import OptionParser
from getpass import getpass
from mechanize import Browser

optsparser = OptionParser()
optsparser.add_option('-o',
		      '--output',
		      default='xml_export.xml',
		      dest='xmlfile',
		      help='Save the xml export to this file '
			   '[default: %default]')
optsparser.add_option('-u',
                      '--username',
                      default=None,
                      dest='user',
                      help='Username')
optsparser.add_option('-p',
                      '--password',
                      default=None,
                      dest='password',
                      help='Password')
options, args = optsparser.parse_args()

# Get username and password
username = options.user
if not username:
    if os.environ.has_key('SFUID'):
        username = os.environ['SFUID']
    else:
        username = raw_input('Enter your SourceForge username: ')

password = options.password
if not password:
    password = getpass('Enter password for \'%s\': ' % username)

# Login to sourceforge
print 'Logging into SourceForge...'
br = Browser()
br.set_handle_robots(False) # don't pay attention to robots.txt
login_url = 'https://sourceforge.net/account/login.php'
xml_url = 'https://sourceforge.net/export/xml_export.php?group_id=71730'
br.open(login_url)
br.select_form('login_userpw')
#br.select_form(nr=2)
br['form_loginname'] = username
br['form_pw'] = password
br.submit()
time.sleep(1)

# Download XML export file
print 'Reading XML...'
response = br.open(xml_url)
xml = response.read()
if len(xml) < 250:
    print 'Unauthorized login or download corrupted. Nothing was saved.'
    sys.exit(-1)

# Save file
xmlfile = open(options.xmlfile, 'w')
xmlfile.write(xml)
xmlfile.close()
print 'XML data saved to %s' % options.xmlfile

