# Sean's website makefile
#

TDIR=tracker
TPROG=sf2wiki.py

SDIR=status
SDATA=$(shell ls -d $(SDIR)/raw/* | grep -v .svn)
SPROG=compile_status.pl

ifdef SFUID
USER=$(SFUID)
endif

SERVER=shell1.sourceforge.net
DIR=/home/groups/o/op/openhpi/htdocs

RSYNC=rsync -rlvC --exclude '.emacs*' --rsh=ssh ./ $(USER)@$(SERVER):$(DIR)
CHMOD=ssh $(USER)@$(SERVER) "find $(DIR) -user $(USER) -exec chmod g+w {} \;"
CHMODD=ssh $(USER)@$(SERVER) "find $(DIR) -user $(USER) -type d -exec chmod g+s {} \;"

all: uptodate status/rollup.html tracker/index.shtml
	$(RSYNC)
	$(CHMOD)
	$(CHMODD)

uptodate:
	svn up
	svn ci

$(SDIR)/$(SPROG):

tracker/index.shtml: tracker/index.tmpl $(shell ls tracker/*py)
	cd $(TDIR) && ./$(TPROG)

status/rollup.html: $(SDATA) $(SDIR)/$(SPROG)
	cd $(SDIR) && ./$(SPROG)
