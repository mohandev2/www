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
This will parse the SF XML export file and create a
structure containing the tracker data which can be used
by other programs.

Author(s):
        Renier Morales <renierm@users.sf.net>
"""
from xml.sax import make_parser, handler, SAXException

class ParseSFExport(handler.ContentHandler):

    def __init__(self, releases, titles=None):
        handler.ContentHandler.__init__(self)
        self._releases = releases
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

        if titles:
            for x in range(len(self._db)):
                self._db[x]['title'] = titles[x]

    def startElement(self, tagname, attrs):	
        if tagname == 'artifact':
            self._artifact = {}
        elif tagname == 'field' and self._artifact != None:
            self._artifact['_name'] = attrs['name']

    def characters(self, content):
        c = content.encode('latin_1', 'ignore').strip()
        artifact = self._artifact
        if artifact != None and artifact.has_key('_name'):
            artifact[artifact['_name']] = \
                artifact.get(artifact['_name'], '') + c
        
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

def get_data(xmlfile, releases, titles=None):
    xmlparser = make_parser()
    xmlparser.setFeature(handler.feature_namespaces, 0)
    parser = ParseSFExport(releases, titles)
    xmlparser.setContentHandler(parser)
    xmlparser.parse(xmlfile)

    return parser._db
