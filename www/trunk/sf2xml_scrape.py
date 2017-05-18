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
capturing all bugs and features for a specific release.

Author(s):
	Renier Morales <renierm@users.sf.net>
	Shyamala Hirepatt <shyamala.hirepatt@hp.com>
	Mohan Devarajulu <mohan@fc.hp.com>

"""
import sys, os, time
from optparse import OptionParser
from mechanize import Browser
from BeautifulSoup import BeautifulSoup
import urllib2
from urllib2 import URLError
import re

# options parsing
optsparser = OptionParser(usage='%prog [options] <release>')
optsparser.add_option('-o',
		      '--output',
		      default='xml_export.xml',
		      dest='xmlfile',
		      help='Save the xml export to this file '
			   '[default: %default]')
options, args = optsparser.parse_args()
if len(args) != 1:
    print 'Did not get a release level (e.g. %s 2.6.0).' % sys.argv[0]
    optsparser.print_help()
    sys.exit()

z = 2
trackers = { 'Bugs': 'bugs/', 'Feature Requests': 'feature-requests/' }
list = ['Ticket Number', 'Summary'];

# output will be written in xml format following SF's export file format
xmlfile = open(options.xmlfile, 'w')
xmlfile.write("<?xml version='1.0' encoding='ISO-8859-1'?>\n")
xmlfile.write('<project_export>\n\n<artifacts>\n\n')

url = 'https://sourceforge.net/p/openhpi/'
br = Browser()
br.clear_history()
br.set_handle_robots(False) # don't pay attention to robots.txt

for x in trackers.keys():
    rows = []
    # Go to page and set to browse specific state and release
    print 'Going to %s tracker' % x
    try:
        response = br.open(url + trackers[x] + "/milestone/" + args[0] + "/?limit=250")
    except urllib2.HTTPError:
	print 'There is no %s release found for %s' % (args[0], x)
        continue
    except urllib2.URLError:
 	raise	
    except:
        print 'There are no %s for the release %s' % (x, args[0])
        continue

    html = response.read()
    soup = BeautifulSoup(html)
    ticket_table = soup.find('table', {'class': 'ticket-list'})

    print 'Getting %s Milestone All %s' % (args[0], x)
    if not ticket_table:
        print 'There are no %s for Release %s' % (x, args[0])
        continue        
    for row in ticket_table.findAll('tr')[1:]:
        for col in row.findAll('td'):
            if col.text == args[0]:
                rows.append(row)
    if not rows:
        print 'There are no %s for Release %s' % (x, args[0])
        continue        

    list_len = len(list)
    for row in rows:
        i = 0
        xmlfile.write('<artifact>\n')
        xmlfile.write('\t<field name="artifact_type">%s</field>\n' % x)
        for col in row.findAll('td'):
            xmlfile.write('\t<field name="%s">%s</field>\n' % (list[i], col.text))
            if list[i] == "Ticket Number":
                url2 = url + trackers[x] + col.text
            i = i + 1
            if i >= list_len:
                break
        response = br.open(url2)
        html = response.read()
        soup = BeautifulSoup(html)
        divs = soup.findAll('div', {'class': 'grid-20 pad'})
        for div in divs:
            grids = div.find('div', {'class': 'view_holder'})
            for grid in grids.findAll('div'):
                mylist = grid.text.split(':')
                if mylist[0] != "":
                    if mylist[0] == "Labels":
                        mylist[1] = mylist[1].split(" (")[0]
                    xmlfile.write('\t<field name="%s">%s</field>\n' % (mylist[0], mylist[1]))
            ticket_content = div.find('div', {'id': 'ticket_content'})
            xmlfile.write('\t<field name="%s">' % "Details")
            lines = 0
            for p in ticket_content.findAll('p'):
                lines = lines + 1
                if lines > 1:
                    xmlfile.write('\n\t\t\t      ')
                xmlfile.write('%s' % str(p.text.encode('utf-8')))
            xmlfile.write('</field>\n')
            discussion = div.find('div', {'id': 'discussion_holder'})
            xmlfile.write('\t<field name="%s">\n' % discussion.h2.text)
            comment = discussion.find('div', {'id': 'comment'})
            for discussion in comment.findAll('div', {'class': 'discussion-post'}):
                xmlfile.write('<message>\n')
                for small in discussion.findAll('small'):
                    try:
                        xmlfile.write('\t\t<field name="%s">%s</field>\n' % ("mod_by", small.a.text))
                    except:
                        xmlfile.write('\t\t<field name="%s">%s</field>\n' % ("entry_date",  small.text))
                for display_post in discussion.findAll('div', {'class': 'display_post'}):
                    xmlfile.write('\t\t<field name="%s">' % "content")
                    lines = 0
                    for li in display_post.findAll('li'):
                        content = li.text
                        content = content.replace('--&gt;', '-->')
                        lines = lines + 1
                        if lines > 1:
                            xmlfile.write('\n\t\t\t\t      ')
                        xmlfile.write('%s' % str(content.encode('utf-8'))) 
                    for p in display_post.findAll('p'):
                        xmlfile.write('%s' % str(p.text.encode('utf-8'))) 
                    xmlfile.write('</field>\n')
                xmlfile.write('</message>\n')
            xmlfile.write('</field>\n')
            xmlfile.write('</artifact>\n') 

xmlfile.write('</artifacts>\n</project_export>\n')
xmlfile.close()
print 'Done. Saved to %s' % options.xmlfile
