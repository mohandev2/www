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
This will parse the SF XML export file and generate a table
showing the status of bugs and feature per release in html.

Author(s):
        Renier Morales <renierm@users.sf.net>
"""
from optparse import OptionParser
from xml.sax import make_parser, handler, SAXException
import sfparser

# List of releases to go in the html report
releases = ['2.7.0']
# Parse options
optsparser = OptionParser(usage='%prog [options] [release [release ...]]')
optsparser.add_option('-f', '--xmlfile',
		      dest='xmlfile',
		      metavar='XMLEXPORTFILE',
		      help='XML file which contains the SF exported data [default: %default]',
		      default='xml_export.xml')
options, args = optsparser.parse_args()

# Get list of releases if specified
if len(args) > 0:
	releases = args
	
# This is for determining what css class name to use for printing the artifact
def get_colors(artifact):
	style = '<style="background-color: %s; color: %s">'
	colors = {'Bad':     ('red', 'black'),
		  'Open':    ('yellow', 'black'),
		  'Pending': ('#11ff00', 'black'),
		  'Closed':  ('#009900', 'white')}
	
	if artifact['status'] != 'Closed':
		if 'Nobody' in artifact['assigned_to']:
			return style % colors['Bad']
		else:
			return style % colors['Open']
	else:
		if artifact['resolution'] != 'Fixed':
			return style % colors['Pending']
		else:
			return style % colors['Closed']

# Go get the parsed data
db = sfparser.get_data(options.xmlfile, releases, ['Features', 'Bugs'])

# Generate the wiki page
url = 'http://sourceforge.net/tracker/?func=detail&aid=%s&group_id=71730&atid='
for release in releases:
	print '==== %s ====' % release
	for x in db:
		if len(x['categories']) == 0: continue
		print "||||||||<tablestyle=\"border: 0\"style=\"border: 0; text-align: center\"> [[BR]]'''~+%s+~''' ||" % x['title']
		curl = url + x['id']
		categories = x['categories'].keys()
		categories.sort()
		for category in categories:
			printed_cat = False
			for artifact in x['categories'][category]:
				if artifact['artifact_group_id'] != release:
					continue
				if artifact['status'] == 'Deleted': continue
				if not printed_cat:
					print "||||||||<(> '''%s''' ||" % category
					printed_cat = True
				aid = artifact['artifact_id']
				aurl = curl % aid
				summary = artifact['summary']
				assigned_to = artifact['assigned_to']
				status = artifact['status']
				resolution = artifact['resolution']
				print '||%s %s ||<bgcolor="#eeeeee"> [%s %s] ||<bgcolor="#eeeeee"> %s ||<bgcolor="#eeeeee"> %s - %s ||' % (get_colors(artifact), aid, aurl, summary, assigned_to, status, resolution)

