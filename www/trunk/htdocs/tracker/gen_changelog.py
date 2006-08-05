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
This will parse the SF XML export file and print the changelog
for the specified version level.

Author(s):
        Renier Morales <renierm@users.sf.net>
"""
import sys
from optparse import OptionParser
from xml.sax import make_parser, handler, SAXException

# Parse options
optsparser = OptionParser(usage='%prog [options] <release>')
optsparser.add_option('-w',
		      '--web',
		      dest='web',
		      help='Produce html output instead of plain text',
		      action='store_true',
		      default=False)
optsparser.add_option('-f',
		      '--file',
		      default='xml_export.xml',
		      dest='xmlfile',
		      help='Parse this xml file for the changelog generation '
			   '[default: %default]')
options, args = optsparser.parse_args()
if len(args) != 1:
	print 'Did not get a release level (e.g. %s 2.6.0).' % sys.argv[0]
	optsparser.print_help()
	sys.exit()
	
# Parse XML
class ParseExport(handler.ContentHandler):

	def __init__(self, release, web):
        	handler.ContentHandler.__init__(self)
        	self._release = release
        	self._web = web        	
        	self._db = [
        			{'title' : 'New Features',
        			 'id' : '532254',
        			 'categories' : {}},
        			 
        			{'title' : 'Fixed Bugs',
        			 'id' : '532251',
        			 'categories' : {}}
        		    ]
        	self._trackers = {'Feature Requests' : 0,
        			   'Bugs' : 1 }
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
        		artifact[artifact['_name']] = artifact.get(
        			artifact['_name'], '') + c        		
        
        def endElement(self, tagname):
        	artifact = self._artifact
        	db = self._db
        	if tagname != 'artifact' or artifact == None: return
        	if (artifact['artifact_group_id'] != self._release or
        	    artifact['status'] != 'Closed' or
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
		if self._web:
			self._print_html()
		else:
			self._print_txt()
	
	def _print_txt(self):
		db = self._db
		print 'Changelog for %s' % self._release
    		print '-'*19
		for x in db:
			print '[%s]' % x['title']
			categories = x['categories'].keys()
			categories.sort()
			for category in categories:
				print '', category
				for artifact in x['categories'][category]:
					print '   %s - %s' % (
						artifact['artifact_id'],
						artifact['summary'])
			print ''
				
	def _print_html(self):
		db = self._db
		sp1 = '\t\t'; sp2 = '\t\t\t'; sp3 = '\t\t\t\t'
		url = 'http://sourceforge.net/tracker/?func=detail&' \
		      'aid=%s&group_id=71730&atid='
		
		print '<!--#include virtual="changelog_head.shtml" -->'
		print sp1+'<h3>Changelog for ' + self._release + '</h3>'
		for x in db:
			print sp1+'<h4>%s</h4>' % x['title']
			print sp1+'<div>'
			curl = url + x['id']
			categories = x['categories'].keys()
			categories.sort()
			for category in categories:
				print sp2+'<strong>%s</strong>' % category
				print sp2+'<ul>'				
				for artifact in x['categories'][category]:	
					aid = artifact['artifact_id']
					aurl = curl % (aid)
					summary = artifact['summary']
					print sp3+'<li><a href=%s>%s</a>' \
					      ' - %s</li>' % (aurl,
					      		      aid,
					      		      summary)
					
				print sp2+'</ul>'
				
			print sp1+'</div>'
		
		print '<!--#include virtual="changelog_bottom.html" -->'


xmlparser = make_parser()
xmlparser.setFeature(handler.feature_namespaces, 0)
xmlparser.setContentHandler(ParseExport(args[0], options.web))
xmlparser.parse(options.xmlfile)
