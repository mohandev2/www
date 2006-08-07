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
from string import Template
from xml.sax import make_parser, handler, SAXException
from time import ctime
import sfparser

# List of releases to go in the html report
releases = ['2.6.1', 'Future', '2.6.0', 'None']
# Parse options
optsparser = OptionParser(usage='%prog [options] [release [release ...]]')
optsparser.add_option('-t', '--template',
		      dest='template',
		      metavar='HTMLTEMPLATE',
		      help='Template file to use for html report [default: %default]',
		      default='index.tmpl')
optsparser.add_option('-o', '--output',
		      dest='output',
		      metavar='OUTPUTFILE',
		      help='HTML report will be written to this filename [default: %default]',
		      default='index.shtml')
optsparser.add_option('-x', '--xmlfile',
		      dest='xmlfile',
		      metavar='XMLEXPORTFILE',
		      help='XML file which contains the SF exported data [default: %default]',
		      default='xml_export.xml')
options, args = optsparser.parse_args()

# Create template object from template file given
template_file = open(options.template, 'r')
template = Template(template_file.read())
template_file.close()

# Get list of releases if specified
if len(args) > 0:
	releases = args
	
# This is for determining what css class name to use for printing the artifact
def get_class(artifact):
	if artifact['status'] != 'Closed':
		if 'Nobody' in artifact['assigned_to']: return 'Bad'
		else: return 'Open'
	else:
		if artifact['resolution'] != 'Fixed': return 'Pending'
		else: return 'Closed'

# Go get the parsed data
db = sfparser.get_data(options.xmlfile, releases, ['Features', 'Bugs'])

# Generate the html page
sp1 = '\t\t'; sp2 = '\t\t\t'; h = ''
url = 'http://sourceforge.net/tracker/?func=detail&aid=%s&group_id=71730&atid='
for release in releases:
	h += '<h4>Release Status for %s</h4>\n' % release
	h += sp1+'<div>\n'+sp1+'<table>\n'
	for x in db:
		h += sp2+'<tr><th colspan="5">%s</th></tr>\n' % x['title']
		curl = url + x['id']
		categories = x['categories'].keys()
		categories.sort()
		for category in categories:
			g = sp2+'<tr><td class="group" colspan="5">%s</td></tr>\n' % category			
			f = ''
			for artifact in x['categories'][category]:
				if artifact['artifact_group_id'] != release:
					continue
				aid = artifact['artifact_id']
				aurl = curl % aid
				summary = artifact['summary']
				assigned_to = artifact['assigned_to']
				status = artifact['status']
				resolution = artifact['resolution']
				f += sp2+'<tr><td class="%s">%s</td>' % (get_class(artifact), aid)
				f += '<td class="summary"><a href="%s">%s</a></td>' % (aurl, summary)
				f += '<td class="owner">%s</td>' % assigned_to
				f += '<td class="status">%s - %s</td></tr>\n' % (status, resolution)
			if f != '':
				h += g + f
	h += sp1+'</table>\n'+sp1+'</div>\n'

output = open(options.output, 'w')
output.write(template.substitute(tracker_data=h, last_modified=ctime()))
output.close()
        		
