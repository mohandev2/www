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
Get parsed data from SourceForge tracker in wiki format. Then, post that
to the wiki on http://www.openhpi.org/Status/OpenhpiBugsFeatures

Author(s):
	Renier Morales <renier@openhpi.org>
"""
import sys, time
from subprocess import Popen, PIPE
from mechanize import Browser
from optparse import OptionParser
from getpass import getpass

optsparser = OptionParser(usage='%prog [options] <release>')
optsparser.add_option('-f',
                      '--xmlfile',
                      default='xml_export.xml',
                      dest='xmlfile',
                      help='Read tracker data from this file '
                           '[default: %default]')
optsparser.add_option('-u',
                      '--username',
                      default=None,
                      dest='user',
                      help='User name')
optsparser.add_option('-p',
                      '--password',
                      default=None,
                      dest='password',
                      help='Password')
options, args = optsparser.parse_args()
if len(args) != 1:
	print 'Did not get a release level (e.g. %s 2.6.0).' % sys.argv[0]
	optsparser.print_help()
	sys.exit()

z = 1
# Capture wiki tracker data
print 'Capturing wiki data...'
popen = Popen('./sf2wiki.py -f %s %s' % (options.xmlfile, args[0]),
	      shell=True,
	      stdout=PIPE)
popen.wait()
wikidata = popen.stdout.read()

# Post it
br = Browser()
br.clear_history()
br.set_handle_robots(False) # don't pay attention to robots.txt
print 'Going to wiki...'
response = br.open('http://www.openhpi.org/Status/OpenhpiBugsFeatures?action=login')
br.select_form(nr=2) # The form we want is the third one
br['name'] = options.user or raw_input('Enter your username: ')
br['password'] = options.password or getpass('Enter password for \'%s\': ' %
					     br['name'])
print 'Loggin in...'
time.sleep(z) # Be nice to the website
response = br.submit()
time.sleep(z)
print 'Editing page...'
response = br.follow_link(url_regex='editor=text')
br.select_form(nr=0)
br['savetext'] = wikidata
time.sleep(z)
print 'Saving page...'
response = br.submit()
print 'Done.'

