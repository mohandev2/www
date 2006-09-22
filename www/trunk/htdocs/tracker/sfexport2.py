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
Navigate to the bugs and features pages for the project
capturing all bugs and features closed for a specific release.

Author(s):
        Renier Morales <renierm@users.sf.net>
"""
import sys, os, time
from optparse import OptionParser
from mechanize import Browser
import re

# options parsing
optsparser = OptionParser(usage='%prog [options] <release>')
optsparser.add_option('-o',
		      '--output',
		      default='xml_export.xml',
		      dest='xmlfile',
		      help='Save the xml export to this file '
			   '[default: %default]')
optsparser.add_option('-s',
		      '--status',
		      dest='status',
                      help='Artifact status to filter on [default: %default]',
                      default='Closed')
options, args = optsparser.parse_args()
if len(args) != 1:
        print 'Did not get a release level (e.g. %s 2.6.0).' % sys.argv[0]
        optsparser.print_help()
        sys.exit()

z = 2
status = options.status
trackers = { 'Bugs': '532251', 'Feature Requests': '532254' }

# rules for parsing html
rules = {
'artifact_id': r'.*<h2>\[ ([0-9]+) \].*',
'submitted_by': r'.*<b>Submitted By:</b>\s+<br>\s+([A-Za-z_, -]+) - <a.*',
'assigned_to': r'.*<b>Assigned To: <a .*?</a></b>\s+<br>\s+([A-Za-z_ -]+[a-z]).*',
'status': r'.*<b>Status: <a .*?</a></b>\s+<br>\s+([A-Z][a-z]+)\s+.*',
'resolution': r'.*<b>Resolution: <a .*?</a></b>\s+<br>\s+([A-Z][a-z]+)\s+.*',
'summary': r'.*<h2>\[ [0-9]+ \] (.*?)</h2>.*',
'open_date': r'.*<b>Date Submitted:</b>\s+<br>\s+([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2})\s+.*',
'category': r'.*<b>Category: <a .*?</a></b>\s+<br>\s+([A-Za-z ]+)\s+.*',
'artifact_group_id': r'.*<b>Group: <a .*?</a></b>\s+<br>\s+([0-9\.]+)\s+.*'
}

# output will be written in xml format following SF's export file format
xmlfile = open(options.xmlfile, 'w')
xmlfile.write("<?xml version='1.0' encoding='ISO-8859-1'?>\n")
xmlfile.write('<!DOCTYPE project_export SYSTEM "http://sourceforge.net/export/sf_project_export_0.1.dtd">\n')
xmlfile.write('<project_export>\n<artifacts>\n')

url = 'http://sourceforge.net/tracker/?group_id=71730&atid='
br = Browser()
br.set_handle_robots(False) # don't pay attention to robots.txt

for x in trackers.keys():
	links = []
	# Go to page and set to browse specific state and release
	print 'Going to %s tracker' % x
	response = br.open(url + trackers[x])
	br.select_form('tracker_browse')
	print 'Looking for %s %s for %s release' % (status, x, args[0])
	control = br.find_control('_status', type='select')
	for item in control.items:
		if item.attrs['contents'] == status: break
	else:
		print '%s state does not exist!' % status
		break	
	br['_status'] = [item.name]
	
	control = br.find_control('_group', type='select')
	for item in control.items:
		if item.attrs['contents'] == args[0]: break
	else:
		print 'None found, moving on.'
		continue
	br['_group'] = [item.name]
	
	time.sleep(z) # Don't get blocked by SF for scraping
	response = br.submit()
	
	# For each page of results, go to each bug/feature and get info
	print 'Getting links'
	for link in br.links(url_regex="func=detail"):
		links.append(link)
	
	print 'Parsing %s pages' % x
	
	for link in links:
		time.sleep(z)
		response = br.follow_link(link)
		# scrape the webpage.
		htmldoc = response.read()
		xmlfile.write('<artifact>\n')
		xmlfile.write('<field name="artifact_type">%s</field>\n' % x)
		for rule in rules.keys():
			cre = re.compile(rules[rule], re.MULTILINE | re.DOTALL)
        		match = cre.match(htmldoc)
			xmlfile.write('<field name="%s">%s</field>\n' % (rule, match.groups()[0]))				
		xmlfile.write('</artifact>\n')	

xmlfile.write('</artifacts>\n</project_export>\n')
xmlfile.close()
print 'Done. Saved to %s' % options.xmlfile
