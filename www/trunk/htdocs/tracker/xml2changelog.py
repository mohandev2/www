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
import sf2xml_parser

# Parse options
optsparser = OptionParser(usage='%prog [options] <release>')
optsparser.add_option('-w',
		      '--web',
		      dest='web',
		      help='Produce wiki output instead of plain text',
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

def print_text(db, args):
	print 'Changelog for %s' % args[0]
    	print '-'*19
	for x in db:
		if len(x['categories']) == 0: continue
		print '[%s]' % x['title']
		categories = x['categories'].keys()
		categories.sort()
		for category in categories:
			c = ' ' + category + '\n'
			a = ''
			for artifact in x['categories'][category]:
				if artifact['status'] != 'Closed': continue
				a += '   %s - %s\n' % (artifact['artifact_id'],
						     artifact['summary'])
			if a != '':
				print c + a,
		print ''
			
def print_html(db, args):
	sp1 = '\t\t'; sp2 = '\t\t\t'; sp3 = '\t\t\t\t'
	url = ('http://sourceforge.net/tracker/?func=detail&'
	       'aid=%s&group_id=71730&atid=')
		
	print '<!--#include virtual="changelog_head.shtml" -->'
	print sp1+'<h3>Changelog for ' + args[0] + '</h3>'
	for x in db:
		if len(x['categories']) == 0: continue
		print sp1+'<h4>%s</h4>' % x['title']
		print sp1+'<div>'
		curl = url + x['id']
		categories = x['categories'].keys()
		categories.sort()
		for category in categories:
			c = sp2+'<strong>%s</strong>\n' % category
			c += sp2+'<ul>\n'
			a = ''
			for artifact in x['categories'][category]:	
				aid = artifact['artifact_id']
				aurl = curl % (aid)
				summary = artifact['summary']
				a += (sp3+'<li><a href=%s>%s</a> - %s</li>\n' %
				      (aurl, aid, summary))
			if a != '':
				print c + a + '</ul>'
			
		print sp1+'</div>'
		
	print '<!--#include virtual="changelog_bottom.html" -->'

def print_wiki(db, args):
	url = ('http://sourceforge.net/tracker/?func=detail&'
               'aid=%s&group_id=71730&atid=')

	print '== Changelog for %s ==' % args[0]
        for x in db:
                if len(x['categories']) == 0: continue
                print '===== %s =====' % x['title']
		curl = url + x['id']
                categories = x['categories'].keys()
                categories.sort()
                for category in categories:
                        c = "'''" + category + "'''\n"
                        a = ''
                        for artifact in x['categories'][category]:
				aid = artifact['artifact_id']
                                aurl = curl % (aid)
                                if artifact['status'] != 'Closed': continue
                                a += ' * [%s %s] - %s\n' % (aurl, aid,
							artifact['summary'])
                        if a != '':
                                print c + a,
                print ''

# Main
db = sfparser.get_data(options.xmlfile, [args[0]])
print_changelog = print_text
#if options.web: print_changelog = print_html
if options.web: print_changelog = print_wiki

print_changelog(db, args)

