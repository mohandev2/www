# Sean's website makefile
#

TDIR=tracker
TPROG=arts2html.pl

SDIR=status
SDATA=$(shell ls -d $(SDIR)/raw/* | grep -v CVS)
SPROG=compile_status.pl

ifdef SFUID
USER=$(SFUID)
endif

SERVER=shell1.sourceforge.net
DIR=/home/groups/o/op/openhpi/htdocs

RSYNC=rsync -rlvC --exclude '.emacs*' --rsh=ssh ./ $(USER)@$(SERVER):$(DIR)
CHMOD=ssh $(USER)@$(SERVER) "find $(DIR) -user $(USER) -exec chmod g+w {} \;"
CHMODD=ssh $(USER)@$(SERVER) "find $(DIR) -user $(USER) -type d -exec chmod g+s {} \;"

#all: 
all: uptodate status/rollup.html tracker/index.shtml
	$(RSYNC)
	$(CHMOD)
	$(CHMODD)

uptodate:
	cvs up -dP
	cvs ci

$(SDIR)/$(SPROG):

tracker/index.shtml: tracker/index.tmpl tracker/tracker.db $(shell ls tracker/*pl)
	cd $(TDIR) && ./$(TPROG)

status/rollup.html: $(SDATA) $(SDIR)/$(SPROG)
	cd $(SDIR) && ./$(SPROG)
