# Sean's website makefile
#


SDIR=status
SDATA=$(shell ls -d $(SDIR)/raw/* | grep -v CVS)
SPROG=compile_status.pl

ifdef SFUID
USER=$(SFUID)
endif

SERVER=shell1.sourceforge.net
DIR=/home/groups/o/op/openhpi/htdocs

RSYNC=rsync -rlvC --exclude '.emacs*' --rsh=ssh ./ $(USER)@$(SERVER):$(DIR)
CHMOD=ssh $(USER)@$(SERVER) "find $(DIR) $(USER) -exec chmod g+w {} \;"
CHMODD=ssh $(USER)@$(SERVER) "find $(DIR) $(USER) -type d -exec chmod g+s {} \;"

all: uptodate status/rollup.html 
	$(RSYNC)
	$(CHMOD)
	$(CHMODD)

uptodate:
	cvs up -dP
	cvs ci

$(SDIR)/$(SPROG):

status/rollup.html: $(SDATA) $(SDIR)/$(SPROG)
	cd $(SDIR) && ./$(SPROG)
