# Sean's website makefile
#

SDIR=status
SDATA=$(shell ls -d $(SDIR)/raw/* | grep -v CVS)
SPROG=compile_status.pl

SERVER=shell1.sourceforge.net
DIR=/home/groups/o/op/openhpi/htdocs

RSYNC=rsync -rlvC --exclude '.emacs*' --rsh=ssh ./ $(SERVER):$(DIR)
CHMOD=ssh $(SERVER) "find $(DIR) -user `whoami` -exec chmod g+w {} \;"
CHMODD=ssh $(SERVER) "find $(DIR) -user `whoami` -type d -exec chmod g+s {} \;"

all: status/rollup.html
	$(RSYNC)
	$(CHMOD)
	$(CHMODD)

$(SDIR)/$(SPROG):

status/rollup.html: $(SDATA) $(SDIR)/$(SPROG)
	cd $(SDIR) && ./$(SPROG)
