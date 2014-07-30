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
        Shyamala Hirepatt <shyamala.hirepatt@hp.com>
        Mohan Devarajulu <mohan@fc.hp.com>
"""
import sys
from optparse import OptionParser
from xml.sax import make_parser, handler, SAXException
import sf2xml_parser

# Parse options
optsparser = OptionParser(usage='%prog [options] <release [release [release ...]]>')
optsparser.add_option('-f', '--xmlfile',
		      dest='xmlfile',
		      metavar='XMLEXPORTFILE',
		      help='XML file which contains the SF exported data [default: %default]',
		      default='xml_export.xml')
options, args = optsparser.parse_args()

# Get list of releases if specified
releases = args
if len(releases) == 0:
    print 'Did not get a release level (e.g. %s 2.6.0).' % sys.argv[0]
    optsparser.print_help()
    sys.exit()

# This is for determining what css class name to use for printing the artifact
def get_colors(artifact):
    style = '<style="background-color: %s; color: %s">'
    colors = {'Bad':     ('red', 'black'),
              'Open':    ('yellow', 'black'),
              'Pending': ('#11ff00', 'black'),
              'Closed':  ('#009900', 'white')}

    if artifact['Status'] != 'closed':
        if 'Nobody' in artifact['Owner']:
            return style % colors['Bad']
        else:
            return style % colors['Open']
    else:
        if artifact['Status'] != 'closed-fixed':
            return style % colors['Pending']
        else:
            return style % colors['Closed']

# Go get the parsed data
db = sf2xml_parser.get_data(options.xmlfile, releases, ['Features', 'Bugs'])

# Generate the wiki page
url = 'http://sourceforge.net/p/openhpi/'
for release in releases:
    print '==== %s ====' % release
    for x in db:
        if len(x['categories']) == 0: continue
        print "||||||||<tablestyle=\"border: 0\"style=\"border: 0\"> '''~+%s+~''' ||" % x['title']
        if (x['title'] == "New Features"):
            curl = url + "feature-requests/"
        else:
            curl = url + "bugs/"
        categories = x['categories'].keys()
        categories.sort()
        for category in categories:
            printed_cat = False
            for artifact in x['categories'][category]:
                if artifact['Milestone'] != release: continue
                if artifact['Status'] == 'Deleted': continue
                if not printed_cat:
                    print "||||||||<(> '''%s''' ||" % category
                    printed_cat = True
                
                aid = artifact['Ticket Number']
                aurl = curl + aid
                summary = artifact['Summary']
                assigned_to = artifact['Owner']
                status = artifact['Status']
                print '||%s %s ||<bgcolor="#eeeeee"> [%s %s] ||<bgcolor="#eeeeee"> %s ||<bgcolor="#eeeeee"> %s ||' % (get_colors(artifact), aid, aurl, summary, assigned_to, status)

