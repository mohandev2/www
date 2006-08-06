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
import sys
from optparse import OptionParser
from string import Template
from xml.sax import make_parser, handler, SAXException
from time import ctime

# List of releases to go in the html report
releases = ['2.6.0', '2.6.1', 'Future', 'None']
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
        
# Parse XML
class ParseExport(handler.ContentHandler):
	def __init__(self, releases, template, output):
        	handler.ContentHandler.__init__(self)
        	self._releases = releases
        	self._template = template
        	self._output = output
        	self._db = [{'title' : 'Features', 'id' : '532254', 'categories' : {}},
			     {'title' : 'Bugs', 'id' : '532251', 'categories' : {}}]
        	self._trackers = {'Feature Requests' : 0, 'Bugs' : 1 }
        	self._artifact = None

	def startElement(self, tagname, attrs):	
        	if tagname == 'artifact':
		       	self._artifact = {}
        	elif tagname == 'field' and self._artifact != None:
       			self._artifact['_name'] = attrs['name']

        def characters(self, content):
        	c = content.encode('latin_1', 'ignore').strip()
        	artifact = self._artifact
        	if artifact != None and artifact.has_key('_name'):
        		artifact[artifact['_name']] = artifact.get(artifact['_name'], '') + c

        def endElement(self, tagname):
        	artifact = self._artifact
        	db = self._db
        	if tagname != 'artifact' or artifact == None: return
        	if (artifact['artifact_group_id'] not in self._releases or
        	    artifact['artifact_type'] not in self._trackers.keys()):
        		del artifact
        		self._artifact = None
        		return
        	
		tpos = self._trackers[artifact['artifact_type']]
		categories = db[tpos]['categories']

		if not categories.has_key(artifact['category']):
			categories[artifact['category']] = []
			
		categories[artifact['category']].append(artifact)			
        	self._artifact = None

	def endDocument(self):
		db = self._db
		sp1 = '\t\t'; sp2 = '\t\t\t'; h = ''
		url = 'http://sourceforge.net/tracker/?func=detail&aid=%s&group_id=71730&atid='
		for release in self._releases:
			h += '<h4>Release Status for %s</h4>\n' % release
			h += sp1+'<div>\n'+sp1+'<table>\n'
			for x in db:
				h += sp2+'<tr><th colspan="5">%s</th></tr>\n' % x['title']
				curl = url + x['id']
				categories = x['categories'].keys()
				categories.sort()
				for category in categories:
					g = sp2+'<tr><td class="group" colspan="5">%s</td></tr>\n' % category
					f = self._print_artifact(x, category, release, curl)
					if f != '':
						h += g + f
			h += sp1+'</table>\n'+sp1+'</div>\n'
			
		output = open(self._output, 'w')
		output.write(template.substitute(tracker_data=h, last_modified=ctime()))
		output.close()
		
			
	def _print_artifact(self, x, category, release, curl):
		sp2 = '\t\t\t'; h = ''
		for artifact in x['categories'][category]:
			if artifact['artifact_group_id'] != release:
				continue
			aid = artifact['artifact_id']
			aurl = curl % aid
			summary = artifact['summary']
			assigned_to = artifact['assigned_to']
			status = artifact['status']
			resolution = artifact['resolution']
			h += sp2+'<tr><td class="%s">%s</td>' % (self._get_class(artifact), aid)
			h += '<td class="summary"><a href="%s">%s</a></td>' % (aurl, summary)
			h += '<td class="owner">%s</td>' % assigned_to
			h += '<td class="status">%s - %s</td></tr>\n' % (status, resolution)
			
		return h
			
	def _get_class(self, artifact):
		if artifact['status'] != 'Closed':
			if 'Nobody' in artifact['assigned_to']: return 'Bad'
			else: return 'Open'
		else:
			if artifact['resolution'] != 'Fixed': return 'Pending'
			else: return 'Closed'


xmlparser = make_parser()
xmlparser.setFeature(handler.feature_namespaces, 0)
xmlparser.setContentHandler(ParseExport(releases, options.template, options.output))
xmlparser.parse(options.xmlfile)
